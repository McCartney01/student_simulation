## Embracing Imperfection: Simulating Students with Diverse Cognitive Levels Using LLM-based Agents

This is the anonymous official repository of the ARR February 25 submission "Embracing Imperfection: Simulating Students with Diverse Cognitive Levels Using LLM-based Agents".

![](images/method.png)

### Getting Started

#### 1. Installation

Git clone our repository and creating conda environment:

```python
conda create -n student python=3.8
conda activate student
pip install -r requirements.txt
```

#### 2. Prepare Your API Key

Prepare you openai api key into the environment:

```
export OPENAI_API_KEY="your key"
```

#### 3. Prepare you data

Prepare you data in the `data` folder:

```
data
---student_1
------train.json
------test.json
---student_2
------train.json
------test.json
...
```

 In the `data` folder, each student has a single folder named with their ID. In each student's folder, it should contain two files: `train.json` and `test.json`. Each file should contain several learning records:

```
# An example of train.json
[
	{
		"problem_id": # unique id of this problem,
		"question": # question stem,
		"desc": # descriptions about this problem, mainly about what concepts it tests,
		"program": # student's code,
		"error_desc": # analysis on student's code. If it's correct, it should be "No error."; otherwise it is a detailed explanation about student's mistakes
	},
	{
	
	},
	...
]
```

#### 4. Run the code

```
python test.py
```

