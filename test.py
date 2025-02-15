import json
from nano_graphrag import GraphRAG, QueryParam
from nano_graphrag.prompt import GRAPH_FIELD_SEP, PROMPTS
import os
import random
from openai_client import multiple_request
from sbs import solve

from concurrent.futures import ThreadPoolExecutor, as_completed
from nano_graphrag._llm import gpt_4o_complete

random.seed(0)


str_model = '4o'
used_model = 'gpt-4o'

first = 'ours'
second = 'ours'

def insert(graph_func, student_id):
    with open(f'data/{student_id}/train.json') as f:
        data = json.load(f)

    input_string = []
    for i in data:
        this_d = PROMPTS['get_library'].format(question=i['question'], desc=i['desc'], program=i['program'], error_desc=i['error_desc'])
        input_string.append(this_d)

    connect_str = "-"*100
    input_string = connect_str.join(input_string)
    tmp = input_string.split(connect_str)
    assert len(tmp)==len(data)
    graph_func.insert(input_string)

def retrieve(graph_func, student_id):
    template = """Question:
    {question}


    Description:
    {desc}"""

    with open(f'data/{student_id}/test.json') as f:
        data = json.load(f)

    retrieve_result = []

    for i in data:
        this_d = template.format(question=i['question'], desc=i['desc'])

        a = graph_func.query(this_d, param=QueryParam(mode="local", only_need_context=True))
        retrieve_result.append(a)
    
    os.makedirs(f'data_{str_model}/{student_id}', exist_ok=True)
    filename = f'data_{str_model}/{student_id}/retrieve.json'
    with open(filename, 'w') as f:
        json.dump(retrieve_result, f, ensure_ascii=False, indent=4)

def generate_desc_for_every_kc(graph_func, working_dir):
    graph = graph_func.chunk_entity_relation_graph._graph
    node = graph.nodes

    messages = []
    mid_file = f'{working_dir}/summarize_kc.json'
    for i in node.data():
        node_name = i[0]
        node_desc = i[1]['description'].split(GRAPH_FIELD_SEP)
        good_cnt, bad_cnt = 0, 0
        for j in node_desc:
            if 'Good' in j or 'GOOD' in j:
                good_cnt += 1
            elif 'Bad' in j or 'BAD' in j:
                bad_cnt += 1
        content = PROMPTS['summarize_kc'].format(kc_name=node_name, good_cnt=good_cnt, bad_cnt=bad_cnt, desc='\n'.join(node_desc))
        messages.append({
            "id": node_name,
            "model": used_model,
            "messages": [{"role": "user", "content": content}],
            "output_file": mid_file,
        })
    multiple_request(messages)


def generate_error_desc(student_id, working_dir):
    with open(f'data/{student_id}/test.json') as f:
        test = json.load(f)

    filename = f'data_{str_model}/{student_id}/retrieve.json'
    with open(filename) as f:
        retrieve = json.load(f)
    
    summarize_kc = {}
    with open(f'{working_dir}/summarize_kc.json') as f:
        for i in f.readlines():
            i = json.loads(i)
            summarize_kc[i['id']] = i['output']['choices'][0]['message']['content']

    messages = []
    os.makedirs(f'data_{str_model}/{student_id}/ours', exist_ok=True)
    mid_file = f'data_{str_model}/{student_id}/ours/predict.json'
    for t, r in zip(test, retrieve):
        retrieved_question = r["text_units_section_list"][1][1]
        retrieved_messages = []
        for i in r['results'][:5]:
            this_kc = i['entity_name']
            this_desc = summarize_kc[this_kc]
            retrieved_messages.append(this_kc + '\n\n' + this_desc)
        retrieved_messages = '\n-----------------\n'.join(retrieved_messages)

        content = PROMPTS['generate_error_desc'].format(summarize_kc=retrieved_messages, case=retrieved_question, problem=t['question'])
        
        messages.append({
            "id": t['problem_id'],
            "model": used_model,
            "messages": [{"role": "user", "content": content}],
            "output_file": mid_file,
        })
    multiple_request(messages)

def post_evaluate(student_id, first=None):
    with open(f'data/{student_id}/test.json') as f:
        test = json.load(f)
    final_data = {}
    for i in test:
        final_data[i['problem_id']] = {}
    
    predict_file = f'data_{str_model}/{student_id}/{first}/predict.json'

    ans, gt = {}, {}
    with open(predict_file) as f:
        for i in f.readlines():
            i = json.loads(i)

            judge = i['output']['choices'][0]['message']['content'].split('\n')[0]
            if 'Yes' in judge:
                final_data[i['id']]['judge_correct'] = False
                ans[i["id"]] = [i['output']['choices'][0]['message']['content']]
            else:
                final_data[i['id']]['judge_correct'] = True
                ans[i["id"]] = ["No error."]

    for i in test:
        if i['error_desc'] == "No error.":
            final_data[i['problem_id']]['gt_correct'] = True
        else:
            final_data[i['problem_id']]['gt_correct'] = False
        gt[i['problem_id']] = [i['error_desc']]

    correct = []
    for key, value in final_data.items():
        if value['judge_correct']==value['gt_correct']:
            correct.append(True)
        else:
            correct.append(False)
    return correct, gt, ans

def get_example(student_id, first):
    with open(f'data/{student_id}/test.json') as f:
        test = json.load(f)

    with open(f'data_{str_model}/{student_id}/retrieve.json') as f:
        retrieve = json.load(f)

    predict = {}
    with open(f'data_{str_model}/{student_id}/{first}/predict.json') as f:
        for i in f.readlines():
            i = json.loads(i)
            predict[i['id']] = i['output']['choices'][0]['message']['content'].split('Error Description')[-1]
    
    problem_list, example_list = [], []
    for t, r in zip(test, retrieve):
        retrieved_question = r["text_units_section_list"][1][1]
        example_code = retrieved_question.split('Student Program:\n')[1].split('Error Description:\n')[0].strip()
        example_question = retrieved_question.split('Question:\n')[1].split('Description:\n')[0].strip()
        example = {
            "question": example_question,
            "program": example_code
        }
        problem = {
            "problem_id": t["problem_id"], 
            "question": t["question"],
            "generate_error_desc": predict[t["problem_id"]],
        }
        problem_list.append(problem)
        example_list.append(example)

    gt = {}
    for j in test:
        gt[j['problem_id']] = [j['program']]

    return problem_list, example_list, gt

def generate_solution(student_list, max_iter=3, max_beam=2, first=None):
    answer, Nodes_list_dict, gt = {}, {}, {}
    futures = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        for student_id in student_list:
            problem_list, example_list, this_gt = get_example(student_id, first=first)
            
            for key, value in this_gt.items():
                gt[student_id+'_'+key] = value

            for problem, example in zip(problem_list, example_list):
                futures.append(executor.submit(lambda p: solve(*p), [student_id, problem, example, max_iter, max_beam, first, used_model, str_model]))

        for job in as_completed(futures):
            problem_id, current_node, Nodes_list, student_id = job.result(timeout=None)
            answer[student_id + '_' + problem_id] = [current_node.answer]
            Nodes_list_dict[problem_id] = Nodes_list
    return gt, answer



def eval_all_1(student_list, first=None, second=None, max_iter=3, max_beam=2):
    gt, answer = generate_solution(student_list, first=first, max_beam=max_beam, max_iter=max_iter)

    messages = []
    for k in student_list:
        eval_file = f'data_{str_model}/{k}/{first}_{second}/depth_{max_iter}_beam_{max_beam}/code_eval.json'

        with open(f'data/{k}/test.json') as f:
            test = json.load(f)
        this_gt, this_answer = {}, {}
        for i in test:
            new_key = k+'_'+i['problem_id']
            assert i['program']==gt[new_key][0]
            content = PROMPTS['eval_code'].format(question=i['question'], gt_code=i['program'], error_desc=i['error_desc'], code=answer[new_key][0])
            messages.append({
                "id": i['problem_id'],
                "model": "o1-mini",
                "messages": [{"role": "user", "content": content}],
                "output_file": eval_file,
            })
            this_gt[new_key] = [i['program']]
            this_answer[new_key] = answer[new_key]

    multiple_request(messages, request_per_minite=80)

    cnt = 0
    for k in student_list:
        eval_file = f'data_{str_model}/{k}/{first}_{second}/depth_{max_iter}_beam_{max_beam}/code_eval.json'
        with open(eval_file) as f:
            for i in f.readlines():
                i = json.loads(i)
                string = i['output']['choices'][0]['message']['content']
                string = string.split('|')[0].split('(')[-1].strip()
                cnt += int(string)

    print(round(cnt/len(gt.keys()),2))

def eval_error_desc_gen(student_list, first=None):
    gt, answer = {}, {}
    correct, messages = [], []
    for k in student_list:
        this_correct, this_gt, this_answer = post_evaluate(k, first=first)
        with open(f'data/{k}/test.json') as f:
            test = json.load(f)

        eval_file = f'data_{str_model}/{k}/{first}/error_eval.json'
        for key, value in this_gt.items():
            new_key = k+'_'+key
            gt[new_key] = value
            answer[new_key] = this_answer[key]
            for i in test:
                if i['problem_id'] == key:
                    content = PROMPTS['eval_error_desc'].format(question=i['question'], gt_code=i['program'], error_desc=i['error_desc'], new_error_desc=this_answer[key])
                    messages.append({
                        "id": key,
                        "model": "o1-mini",
                        "messages": [{"role": "user", "content": content}],
                        "output_file": eval_file,
                    })
                    break
        correct += this_correct
    print(round(sum(correct)/len(correct),2))
    
    multiple_request(messages, request_per_minite=80)

    cnt = 0
    
    for k in student_list:
        eval_file = f'data_{str_model}/{k}/{first}/error_eval.json'
        with open(eval_file) as f:
            for i in f.readlines():
                i = json.loads(i)
                string = i['output']['choices'][0]['message']['content']
                string = string.split('|')[0].split('(')[-1].strip()
                cnt += int(string)
                
    print(round(cnt/len(gt.keys()),2))

student_list = []
for i in os.listdir('data'):
    if i!='.DS_Store':
        student_list.append(i)

for student_id in student_list:
    working_dir = f'data_{str_model}/student/{student_id}'
    graph_func = GraphRAG(working_dir=working_dir, best_model_func=gpt_4o_complete, cheap_model_func=gpt_4o_complete)
    insert(graph_func, student_id)
    generate_desc_for_every_kc(graph_func, working_dir)
    retrieve(graph_func, student_id)
    generate_error_desc(student_id, working_dir)

gt, ans = generate_solution(student_list, first=first)
eval_all_1(student_list=student_list, first=first, second=second, max_iter=3, max_beam=2)