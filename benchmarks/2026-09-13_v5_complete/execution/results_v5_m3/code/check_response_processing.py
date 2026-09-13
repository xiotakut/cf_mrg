import sys,logging,json,time
from pathlib import Path
sys.path.insert(0,'/home/data3/txy/MA-RAG')
from microservice import CustomLanguageModel
from utils import process_response as original
from response_processing import process_response as optimized
from prepare import OUT
m=CustomLanguageModel('qwen3-8b',logging.getLogger(__name__),base_url='http://127.0.0.1:8011/v1')
records=[]
for thinking,n in [(False,8),(True,1)]:
    response=m.generate([dict(role='user',content='Explain why ice floats on liquid water, then conclude with <answer>density</answer>.')],temperature=0 if thinking else .7,max_new_tokens=256,enable_thinking=thinking,top_logprobs=20,n=n)
    t=time.perf_counter();old=original(response);a=time.perf_counter()-t
    t=time.perf_counter();new=optimized(response);b=time.perf_counter()-t
    assert old==new
    records.append(dict(thinking=thinking,candidates=n,compared_tokens=sum(len(r['token_entropies']) for r in old),original_seconds=a,optimized_seconds=b,all_response_fields_exact_equal=True))
(OUT/'response_processing_validation.json').write_text(json.dumps(dict(status='passed',records=records),indent=2)+'\n')
print(records)
