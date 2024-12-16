import re
# from rouge import Rouge
from pycocoevalcap.rouge.rouge import Rouge
from pycocoevalcap.cider.cider import Cider
from pycocoevalcap.bleu.bleu import Bleu
import argparse
import os
import json
import numpy as np



def evaluate_captioning(gt, ans):
    rouge = Rouge()
    cider = Cider()
    bleu = Bleu(4)
    
    rouge_score, rouge_scores = rouge.compute_score(gt, ans)
    cider_score, cider_scores = cider.compute_score(gt, ans)
    blue_score, blue_scores = bleu.compute_score(gt, ans)

    eval_list = []
    cnt = 0
    for key, value in gt.items():
        eval_list.append({
            "id": key,
            "rouge": rouge_scores[cnt],
            "cider": cider_scores[cnt],
            "bleu4": blue_scores[-2][cnt],
        })
        cnt += 1

            
    results = {'rouge': round(rouge_score*100,2), 'cider': round(cider_score*100,2), 'bleu4': round(blue_score[-1]*100,2)}
    print(results)
    return results, eval_list