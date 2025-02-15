from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import time
from datetime import datetime
import json


def test(id, data, interval=1):
    time.sleep(id * interval)

    real_id = data["id"]
    start = time.time()
    print(f"[{datetime.now()}] task {real_id} start.\n")
    try:
        if 'generation_config' in data:
            generation_config = data['generation_config']
        else:
            generation_config = {}

        if 'text-embedding' in data["model"]:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), timeout=60)
            stream = client.embeddings.create(
                model=data["model"],
                input=data["messages"],
                encoding_format="float"
            ).to_dict()
        else:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), timeout=60)
            stream = client.chat.completions.create(
                model=data["model"],
                messages=data["messages"],
                **generation_config,
            ).to_dict()
        
        output_data = {
            "id": real_id,
            "output": stream,
            "input": data
        }
        with open(data["output_file"], 'a') as f:
            f.write(json.dumps(output_data, ensure_ascii=False)+'\n')

        print(f"[{datetime.now()}] task {real_id} finish in {round(time.time() - start, 3)} Seconds.\n")
        finished = True
    except Exception as error:
        print(f"[{datetime.now()}] task {real_id} failed: ", repr(error))
        print("\n")
        finished = False
    
    return finished, data

def multiple_request(messages, request_per_minite=200, max_round=10):
    """
    messages: List, each item is a dict:
    id: int
    messages: [{"role": "user", "content": str}]
    model: str
    output_file: str
    generation_config: dict
    """

    tmp_messages = []
    for i in messages:
        finished = False
        if os.path.isfile(i["output_file"]):
            with open(i["output_file"]) as f:
                finished_data = [json.loads(j) for j in f.readlines()]
            for j in finished_data:
                if j["id"]==i["id"]:
                    finished = True
        if not finished:
            tmp_messages.append(i)
    
    if len(tmp_messages)==0:
        return
    
    print(f"[{datetime.now()}] Start Processing with {len(tmp_messages)} Tasks.\n")

    interval = 60 / request_per_minite
    for this_round in range(max_round):
        start = time.time()
        if len(tmp_messages)==0:
            break
        failed_messages = []
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = [executor.submit(lambda p: test(*p), [i, data, interval]) for i, data in enumerate(tmp_messages)]
            for job in as_completed(futures):
                res, data = job.result(timeout=None)  # 默认timeout=None，不限时间等待结果
                if not res:
                    failed_messages.append(data)
            
            print(f"[{datetime.now()}] Round {this_round+1} Finished in {round(time.time() - start, 3)} Seconds, {len(tmp_messages)-len(failed_messages)} Tasks Succeed, {len(failed_messages)} Tasks Failed.\n")
            tmp_messages = failed_messages
        time.sleep(1)