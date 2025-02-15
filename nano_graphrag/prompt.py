GRAPH_FIELD_SEP = "<SEP>"
PROMPTS = {}

PROMPTS["summarize_kc"] = """-Goal-
You are tasked with evaluating a student’s understanding of a specific concept based on several descriptions derived from their past problem-solving records. Each description corresponds to a specific question and is categorized as either:
	•	Good: Demonstrates correct understanding or application of the concept.
	•	Bad: Indicates misunderstanding or errors in applying the concept.

Each description includes detailed text explaining the student’s performance on that question. Your goal is to provide an overall evaluation based on both Good and Bad descriptions.

-Steps-:
Based on the input descriptions, provide:
1.	A Score (1-5):
	•	1: No understanding; critical misconceptions.
	•	2: Poor understanding; partial grasp but significant issues.
	•	3: Moderate understanding; grasp of core concepts but notable errors.
	•	4: Good understanding; minor mistakes.
	•	5: Excellent understanding; strong grasp and correct application.
The score should consider the frequency and severity of Good and Bad descriptions, as well as the details they convey.
2.	A Written Evaluation:
Provide a single, comprehensive paragraph summarizing the student’s overall performance. This should include their strengths and weaknesses in a balanced manner, without separating them explicitly or including suggestions.

-Output Format-
Score: (you score)

Evaluation: (your evaluation)

-Real Data-
Knowledge Point: {kc_name}

There are {good_cnt} positive descriptions, {bad_cnt} negative descriptions.
Descriptions:
{desc}
"""

PROMPTS["eval_code"] = """You are given a Python programming question, a student's answer code, and an analysis of errors found in the code. Then, I will provide a new code. Your task is to evaluate the new code and determine how well it reproduces the described errors. Please assign a score from 1 to 5, where:

•	1: The new code does not reproduce the described errors at all.
•	2: The new code attempts to reproduce some the described errors but fails significantly.
•	3: The new code somewhat reproduces some described errors but with significant differences.
•	4: The new code reproduces most the described errors well, with a little differences.
•	5: The new code fully and naturally reproduces the described errors.

Additionally, please provide a brief explanation within 3 sentences justifying your score, focusing on how closely the new code matches the nature of the described error.

Format your output as (Score | Explanation), such as (5 | The new code successfully reproduces the described errors). Do not output any other words.

-Real Data-
Question:
{question}

Student's answer code:
{gt_code}

Error Analysis:
{error_desc}

New Code:
{code}

Output:
"""

PROMPTS["eval_error_desc"] = """You are given a Python programming question, a student's answer code, and an analysis of errors found in the code. Then, I will provide a new error analysis. Your task is to evaluate the new analysis and determine how accurate and reasonable it is and how closely it matches the original error analysis. Please assign a score from 1 to 5, where:

•	1: The new analysis is completely unreasonable and unrelated to the actual error.
•	2: The new analysis attempts to describe the error but fails significantly or introduces unrelated issues.
•	3: The new analysis somewhat aligns with the actual error, but there are noticeable inaccuracies or omissions.
•	4: The new analysis is mostly accurate and aligns well with the actual error, with only minor differences or slight deviations.
•	5: The new analysis is fully accurate, natural, and matches the actual error explanation closely.

Additionally, please provide a brief explanation within 3 sentences justifying your score, focusing on the accuracy, relevance, and clarity of the new analysis in comparison to the original.

Format your output as (Score | Explanation), such as (5 | The new analysis is fully accurate). Do not output any other words.

-Real Data-
Question:
{question}

Student's answer code:
{gt_code}

Error Analysis:
{error_desc}

New Error Analysis:
{new_error_desc}

Output:
"""

PROMPTS["get_library"] = """Question:
{question}


Description:
{desc}


Student Program:
{program}


Error Description:
{error_desc}"""


PROMPTS["generate_error_desc"] = """-Goal-
Background:
You are tasked with predicting whether a student will make mistakes on a new Python programming problem. The input includes:
1.	Student’s Understanding: A summary of the student’s grasp of relevant concepts, including their overall strengths and weaknesses.
2.	Historical Case Study: A Python problem the student has previously attempted, which serves as a reference. This case study includes:
	•	Problem statement.
	•	Concepts the problem tests.
	•	Student’s code.
	•	Error analysis of the student’s submission, detailing the mistakes and their nature.
3.	New Problem: A Python problem that the student has not yet attempted.

The historical case study provides additional context about the student’s problem-solving patterns, common mistakes, and conceptual gaps, which must be considered along with their general understanding.

-Steps-
1.	Error Prediction: Analyze the student’s understanding and historical case study to predict whether the student is likely to make mistakes on the new problem.
	•	Compare the concepts tested in the new problem with the student’s strengths, weaknesses, and past errors.
	•	Use the historical case study to identify recurring patterns or tendencies in the student’s approach to problem-solving.
Simply output 'Yes' or 'No'
2.	Error Description: Provide an error description similar to the style of the historical case.
	•	Use the style of error descriptions from the historical case study as a reference.
	•	Ensure that the error descriptions are related to the new problem.

-Output Format-
Error Prediction: (Yes/No)

Error Description: (Your detailed analysis)

-Real Data-
Student's Understanding:
{summarize_kc} 

Historical Case Study:
{case}

New Problem:
{problem}:

Output:
"""

PROMPTS["refine_error_desc"] = """-Goal-
Given a student’s error description, please rewrite it to be concise and specific, focusing on clear problem identification without background analysis or speculation.

1.	Directly state the specific issue without detailed background or likelihood analysis.
2.	Avoid speculative phrases.
3.	Focus on pointing out specific problems instead of analyzing their causes.
4.  Maintain the original semantics and formatting.
5.  If the original error description identifies no errors, simply output "No error." without any other words.

Directly output your refined error descriptions.

-Real Data-
Origianl Error Description:
{error_desc}

Refined Error Description:
"""

PROMPTS[
    "claim_extraction"
] = """-Target activity-
You are an intelligent assistant that helps a human analyst to analyze claims against certain entities presented in a text document.

-Goal-
Given a text document that is potentially relevant to this activity, an entity specification, and a claim description, extract all entities that match the entity specification and all claims against those entities.

-Steps-
1. Extract all named entities that match the predefined entity specification. Entity specification can either be a list of entity names or a list of entity types.
2. For each entity identified in step 1, extract all claims associated with the entity. Claims need to match the specified claim description, and the entity should be the subject of the claim.
For each claim, extract the following information:
- Subject: name of the entity that is subject of the claim, capitalized. The subject entity is one that committed the action described in the claim. Subject needs to be one of the named entities identified in step 1.
- Object: name of the entity that is object of the claim, capitalized. The object entity is one that either reports/handles or is affected by the action described in the claim. If object entity is unknown, use **NONE**.
- Claim Type: overall category of the claim, capitalized. Name it in a way that can be repeated across multiple text inputs, so that similar claims share the same claim type
- Claim Status: **TRUE**, **FALSE**, or **SUSPECTED**. TRUE means the claim is confirmed, FALSE means the claim is found to be False, SUSPECTED means the claim is not verified.
- Claim Description: Detailed description explaining the reasoning behind the claim, together with all the related evidence and references.
- Claim Date: Period (start_date, end_date) when the claim was made. Both start_date and end_date should be in ISO-8601 format. If the claim was made on a single date rather than a date range, set the same date for both start_date and end_date. If date is unknown, return **NONE**.
- Claim Source Text: List of **all** quotes from the original text that are relevant to the claim.

Format each claim as (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)

3. Return output in English as a single list of all the claims identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

-Examples-
Example 1:
Entity specification: organization
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
{completion_delimiter}

Example 2:
Entity specification: Company A, Person C
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
{record_delimiter}
(PERSON C{tuple_delimiter}NONE{tuple_delimiter}CORRUPTION{tuple_delimiter}SUSPECTED{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}Person C was suspected of engaging in corruption activities in 2015{tuple_delimiter}The company is owned by Person C who was suspected of engaging in corruption activities in 2015)
{completion_delimiter}

-Real Data-
Use the following input for your answer.
Entity specification: {entity_specs}
Claim description: {claim_description}
Text: {input_text}
Output: """

PROMPTS[
    "community_report"
] = """You are an AI assistant that helps a human analyst to perform general information discovery. 
Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.

# Goal
Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.

# Report Structure

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
            ...
        ]
    }}

# Grounding Rules
Do not include information where the supporting evidence for it is not provided.


# Example Input
-----------
Text:
```
Entities:
```csv
id,entity,type,description
5,VERDANT OASIS PLAZA,geo,Verdant Oasis Plaza is the location of the Unity March
6,HARMONY ASSEMBLY,organization,Harmony Assembly is an organization that is holding a march at Verdant Oasis Plaza
```
Relationships:
```csv
id,source,target,description
37,VERDANT OASIS PLAZA,UNITY MARCH,Verdant Oasis Plaza is the location of the Unity March
38,VERDANT OASIS PLAZA,HARMONY ASSEMBLY,Harmony Assembly is holding a march at Verdant Oasis Plaza
39,VERDANT OASIS PLAZA,UNITY MARCH,The Unity March is taking place at Verdant Oasis Plaza
40,VERDANT OASIS PLAZA,TRIBUNE SPOTLIGHT,Tribune Spotlight is reporting on the Unity march taking place at Verdant Oasis Plaza
41,VERDANT OASIS PLAZA,BAILEY ASADI,Bailey Asadi is speaking at Verdant Oasis Plaza about the march
43,HARMONY ASSEMBLY,UNITY MARCH,Harmony Assembly is organizing the Unity March
```
```
Output:
{{
    "title": "Verdant Oasis Plaza and Unity March",
    "summary": "The community revolves around the Verdant Oasis Plaza, which is the location of the Unity March. The plaza has relationships with the Harmony Assembly, Unity March, and Tribune Spotlight, all of which are associated with the march event.",
    "rating": 5.0,
    "rating_explanation": "The impact severity rating is moderate due to the potential for unrest or conflict during the Unity March.",
    "findings": [
        {{
            "summary": "Verdant Oasis Plaza as the central location",
            "explanation": "Verdant Oasis Plaza is the central entity in this community, serving as the location for the Unity March. This plaza is the common link between all other entities, suggesting its significance in the community. The plaza's association with the march could potentially lead to issues such as public disorder or conflict, depending on the nature of the march and the reactions it provokes."
        }},
        {{
            "summary": "Harmony Assembly's role in the community",
            "explanation": "Harmony Assembly is another key entity in this community, being the organizer of the march at Verdant Oasis Plaza. The nature of Harmony Assembly and its march could be a potential source of threat, depending on their objectives and the reactions they provoke. The relationship between Harmony Assembly and the plaza is crucial in understanding the dynamics of this community."
        }},
        {{
            "summary": "Unity March as a significant event",
            "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in the community's dynamics and could be a potential source of threat, depending on the nature of the march and the reactions it provokes. The relationship between the march and the plaza is crucial in understanding the dynamics of this community."
        }},
        {{
            "summary": "Role of Tribune Spotlight",
            "explanation": "Tribune Spotlight is reporting on the Unity March taking place in Verdant Oasis Plaza. This suggests that the event has attracted media attention, which could amplify its impact on the community. The role of Tribune Spotlight could be significant in shaping public perception of the event and the entities involved."
        }}
    ]
}}


# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
```
{input_text}
```

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
            ...
        ]
    }}

# Grounding Rules
Do not include information where the supporting evidence for it is not provided.

Output:
"""

PROMPTS["entity_extraction"] = """-Goal-
Given a Python programming question along with a description of the skills it tests, and provided with a student’s answer and its evaluation (including whether there are errors and their descriptions), extract all the Python programming knowledge points involved and assess the student’s understanding of each knowledge point.

-Steps-
1. Identify the Python programming knowledge points involved in solving the problem and those present in the student’s code. Then, based on the student’s code and strictly following the error descriptions, evaluate the student’s level of understanding of each knowledge point. Knowledge points not mentioned in the error descriptions can be considered as areas where the student has a good grasp. For each identified knowledge point, extract the following information:
- entity_name: Name of the knowledge point, capitalized
- entity_master_level: Evaluate how well the student understand and master this knowledge point. Choose from 'Good' or 'Bad'
- entity_master_description: Describe how well the student understand and master this knowledge point using a sentence.
Format each knowledge point as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_master_level>{tuple_delimiter}<entity_master_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other. The relationship should be functional, aiding learners in understanding the knowledge. We define 4 types of the relations and you must choose one:
    a) Prerequisite-of: This dual-purpose relationship implies that one entity is either a characteristic of another or a required precursor for another. For instance, "The ability to code is a prerequisite of software development."
    b) Used_for: This dual-purpose relationship indicates that one entity serves as a tool, means, or resource to achieve or perform another. For example, "Mathematics is used for solving engineering problems."
	c) Hyponym_of: This hierarchical relationship signifies that one entity represents a specific instance or subtype within the broader scope of another. For instance, "A rectangle is a hyponym of a polygon."
	d) Part_of: This compositional relationship suggests that one entity constitutes a component or integral section of a larger whole. For example, "A wheel is part of a car."
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_type: type of the relationship, as defined above
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationshp_type>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)

3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

######################
-Examples-
######################
Example 1:

Input:
Question:
Input a positive integer n (n>=2), and output the sum of all n-digit prime numbers. For example, if n=2, the output is the sum of all prime numbers between 10 and 99.

### Input Format:

A positive integer n (n>=2)

### Output Format:

Output the sum of all n-digit prime numbers

### Sample Input:

```in
2
```

### Sample Output:

```out
10-99之间所有的素数和=1043
```


Description:
This problem tests understanding of the `break` statement used to control loops to efficiently determine prime numbers. Students need to implement algorithms to check for prime numbers using loops, applying `break` when a divisor is found. This also requires knowledge of loops, conditionals, and range handling to sum n-digit primes.


Student Program:
m=int(input('请输入一个整数:'))
n=int(input('请输入一个整数：'))
def is_price(m,n):
    sum=0
    for i in range(m,n):
        if i>1:
            for j in range(2,i):
                if i%j==0:
                    break
            else:
                print(i,end=' ')
                sum+=i
    print()
    print("和为：",sum)



Error Description:
1. The function `is_price(m, n)` is defined but never called.
2. The code is asking for two integers `m` and `n`, but should only accept one integer `n`.
3. The range `range(m, n)` is not appropriate for finding all `n`-digit numbers.
4. The code includes Chinese characters in the `input` prompts and `print` statements without an encoding declaration.
5. The variable `sum` conflicts with the Python built-in function name.
################
Output:
("entity"{tuple_delimiter}FUNCTION_DEFINITION{tuple_delimiter}Good{tuple_delimiter}The student successfully defined the function is_price(m, n) with proper syntax, indicating a good understanding of function definition.){record_delimiter}
("entity"{tuple_delimiter}FUNCTION_CALL{tuple_delimiter}Bad{tuple_delimiter}The function is_price(m, n) is never called, showing a lack of understanding of how to utilize defined functions in Python.){record_delimiter}
("entity"{tuple_delimiter}INPUT_HANDLING{tuple_delimiter}Bad{tuple_delimiter}The code incorrectly takes two inputs (m and n) instead of one, demonstrating confusion about the problem’s input requirements.){record_delimiter}
("entity"{tuple_delimiter}RANGE_HANDLING{tuple_delimiter}Bad{tuple_delimiter}The student incorrectly defines the range range(m, n) instead of determining the range of all n-digit numbers, indicating insufficient understanding of range handling for this problem.){record_delimiter}
("entity"{tuple_delimiter}LOOP_CONTROL{tuple_delimiter}Good{tuple_delimiter}The student uses a nested loop and the break statement correctly to identify prime numbers, showing a good grasp of loop control.){record_delimiter}
("entity"{tuple_delimiter}VARIABLE_NAMING{tuple_delimiter}Bad{tuple_delimiter}The variable sum conflicts with Python’s built-in function name, reflecting poor variable naming practices.){record_delimiter}
("entity"{tuple_delimiter}OUTPUT_FORMATTING{tuple_delimiter}Bad{tuple_delimiter}The code includes Chinese characters in the input prompts and print statements without encoding declaration, causing potential issues when running the program in non-Chinese environments.){record_delimiter}
("relationship"{tuple_delimiter}FUNCTION_CALL{tuple_delimiter}FUNCTION_DEFINITION{tuple_delimiter}Used_for{tuple_delimiter}A function call utilizes the defined function to execute its logic, making function calls essential for function definitions to have utility.{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}RANGE_HANDLING{tuple_delimiter}INPUT_HANDLING{tuple_delimiter}Prerequisite-of{tuple_delimiter}Correct input handling is a prerequisite for determining the appropriate range for n-digit numbers.{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}LOOP_CONTROL{tuple_delimiter}RANGE_HANDLING{tuple_delimiter}Used_for{tuple_delimiter}Loop control depends on properly defined ranges to iterate over the correct set of numbers.{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}VARIABLE_NAMING{tuple_delimiter}OUTPUT_FORMATTING{tuple_delimiter}Part_of{tuple_delimiter}Proper variable naming contributes to clear and readable output formatting.{tuple_delimiter}6){completion_delimiter}

######################
-Real Data-
######################
Input: 
{input_text}
################
Output:
"""


PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""


PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["organization", "person", "geo", "event"]
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS[
    "local_rag_response"
] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.

---Target response length and format---

{response_type}


---Data tables---

{context_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.

If you don't know the answer, just say so. Do not make anything up.

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS[
    "global_map_rag_points"
] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1...", "score": score_value}},
        {{"description": "Description of point 2...", "score": score_value}}
    ]
}}

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.


---Data tables---

{context_data}

---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1", "score": score_value}},
        {{"description": "Description of point 2", "score": score_value}}
    ]
}}
"""

PROMPTS[
    "global_reduce_rag_response"
] = """---Role---

You are a helpful assistant responding to questions about a dataset by synthesizing perspectives from multiple analysts.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}


---Analyst Reports---

{report_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


#### previous simulation work comparison
PROMPTS["sim_emnlp_abs"] = """You will be shown a Python programming problem, and predict that whether a student of level {X} would correctly solve the problem. Please remind that a student's level ranges from 1 to 5, while 1 indicates the lowest ability and 5 indicates the highest ability. Directly output your prediction. If you think the student will make mistakes, provide possible details about the mistakes.

-Output Format-
Error Prediction: (Yes/No)

Error Description: (Your detailed analysis)

-Real Data-
Problem:
{problem}
"""


PROMPTS["sim_emnlp_abs_sample"] = """You will be shown a Python programming problem, and predict that whether a student of level {X} would correctly solve the problem. Please remind that a student's level ranges from 1 to 5, while 1 indicates the lowest ability and 5 indicates the highest ability. Directly output your prediction. If you think the student will make mistakes, provide possible details about the mistakes. Use the student's historical case study as a reference.


-Output Format-
Error Prediction: (Yes/No)

Error Description: (Your detailed analysis)

-Real Data-
Historical Case Study:
{case}

Problem:
{problem}
"""