import os, openai, json, tiktoken, time

#todo improvement - dát try/except na openai.error.RateLimitError - počkat a pokračovat od posledního úseku (tzn někde ukládat do slovníku již zpracované nebo počítat odstavce a na začátku přeskočit daný počet odstavců)
# dělit text do tokenů
# počítat tokeny pro rate limit

#načte nastavení a patřičné proměnné

with open('settings.json','r', encoding="utf-8") as file:
    settings = json.loads(file.read())

list_to_exclude = settings['listToExclude']
api_key = settings['apiKey']
model_engine = settings['modelEngine']
prompt = settings['prompt']
include_replacement = settings['includeReplacement'][0]
file_name = settings['inputName']
result_name = settings['resultName']
replacements = settings['replacements']
temp = settings['temperature']
gpt_annoucements_to_exclude = settings['gptExclude']
too_short = settings['tooShort']

if model_engine == 'gpt-3.5-turbo':
    model_context = 4096
elif model_engine == 'gpt-3.5-turbo-16k':
    model_context = 4096*4

elif model_engine == 'gpt-4':
    model_context = 4096*2 #8k

print('Použitý model: ' + str(model_engine))
print('Počet tokenů v kontextu: ' + str(model_context))


rate_limit_per_minute = 200 #kolikrát můžeme poslat request - podle gpt4 - https://platform.openai.com/account/rate-limits
rate_limit_tokens = 10000
necessary_delay = 60.0 / rate_limit_per_minute

openai.api_key = api_key

max_tokens_per_request = int(model_context*0.4)

#funkce, která posílá kousky textu do GPT API

def generate_text_from_paragraphs(paragraph, prompt):
    #prompt += "\n\n" + "\n\n".join(paragraphs)
    
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[{"role": "user", "content": prompt},{"role": "user", "content": paragraph}],
        max_tokens=int(model_context*0.5), # The maximum number of tokens to generate in the chat completion.
        temperature=temp,
        n = 1,
        stop=None,
        timeout=5
    )
    message = response['choices'][0]['message']['content']
    return message

def count_tokens (string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_engine)
    num_tokens = len(encoding.encode(string))
    return num_tokens

#načte zdrojový text a rozkouskuje ho po odstavcích (enter na konci řádku)

with open(file_name, 'r', encoding="utf-8") as file:
    text = file.read()

paragraphs_raw = []

for line in text.split("\n"): # přidáme vše do seznamu po jednotlivých řádcích
    paragraphs_raw.append(line)

paragraphs= []
skip = []

# příprava textu - pokud je moc krátký, nebudeme jej posílat do GPT, ale zkusíme před tím přidat další odstavec
#zároveň kontrolujeme, zda na řádku není něco, co chceme přeskakovat nebo nahrazovat
#co nechceme poslat do GPT je označeno jako False nebo 'kratky' na začátku

for i in range(len(paragraphs_raw)):
    if len(paragraphs_raw[i])<1:
        pass
    if i in skip:
        continue
    if any(substring in paragraphs_raw[i] for substring in list_to_exclude): #kontroluje, zda v textu je nějaký řetězec, který jej diskvalifikuje z odeslání do GPT
        for substring2 in list_to_exclude:
            if substring2 in paragraphs_raw[i]:
                if include_replacement == True and substring2 in replacements: #pokud máme nastavenou náhradu za takový kousek textu, tak ji aplikuje, jinak dá originální znění
                    inter_text = replacements[substring2]
                else:
                    inter_text = (paragraphs_raw[i])
                paragraphs.append([False,inter_text])

    elif len(paragraphs_raw[i])<too_short: #pokud je odstavec moc krátký, GPT by to zmátlo, tak zkusíme přidat další nebo jej pouze zkopírujeme
        temporary_text = paragraphs_raw[i] #základem je text z aktuálního odstavce
        for j in range(i+1,len(paragraphs_raw)):
            if any(substring in paragraphs_raw[j] for substring in list_to_exclude) or count_tokens(temporary_text)+count_tokens(paragraphs_raw[j]) >= max_tokens_per_request: 
                #kontrolujeme následující odstavec na vyloučené výrazy nebo na celkové množství tokenů, pokud něco z toho je pravda, odstavec už nezařadíme
                
                if len(temporary_text) < too_short: # zároveň je zatím poskládaný text moc krátký, dáme odpovídající příznak
                    paragraphs.append(['kratky',temporary_text])
                else: 
                    paragraphs.append([True,temporary_text]) #prozatimní text je ok dlouhý, zapíšeme ho a ujistíme se, že se nezapíše dvakrát
                
                to_add = False
                break
            
            else:
                temporary_text = temporary_text + '\n' + paragraphs_raw[j] #nic nebrání přidat další kousek textu
                to_add = True
                skip.append(j)
        
        if to_add == True:
            paragraphs.append([True,temporary_text])
        

    else:
        paragraphs.append([True,paragraphs_raw[i]])

generated_text = ""

with open('pokus.txt', 'a', encoding='utf-8') as file: # na závěr smyčky přidá text na konec souboru s výsledkem, postupně tak přidává jednotlivé odstavce
    file.write(str(paragraphs))

print('Naporcováno a připraveno k magii...' + '\n')

#smyčka, která rozkouskovaný text postupně dávkuje funkci pro zpracování v GPT

for i in range(len(paragraphs)):
    if paragraphs[i][0] == 'kratky': 
        
        #pokud je odstavec moc krátký, GPT by to zmátlo, tak jej jen zkopírujeme
        
        print('Text je hodně krátký. Vložím raději originál:' + '\n')
        print(paragraphs[i][1] + '\n\n')
        generated_text = (paragraphs[i][1] + '\n\n')
        gpt_processed = False

    elif paragraphs[i][0] == False: 
        
        #kontroluje, zda v textu je nějaký řetězec, který jej diskvalifikuje z odeslání do GPT
        #pokud máme nastavenou náhradu za takový kousek textu, tak ji aplikuje, jinak dá originální znění
        
        print('Tohle nechceme posílat, vkládám co je připraveno nebo originál:' + '\n')
        print(paragraphs[i][1] + '\n\n')

        generated_text = (paragraphs[i][1] + '\n\n')
        gpt_processed = False

    elif paragraphs[i][0] == True:
        print('Předávám text do GPT...' + '\n') #předání textu do GPT
        t = time.time()
        gpt_text = generate_text_from_paragraphs(paragraphs[i][1], prompt) + '\n\n'
        print('GPT: ' + gpt_text)
        gpt_processed = True

        if any(correct_info in gpt_text for correct_info in gpt_annoucements_to_exclude): #pokud GPT vyplivnul nějaké moudro, které máme nastaveno, že nechceme slyšet, tak raději vloží originální text
            print('Prý' + gpt_text + '\n' + '...' + '\n' 'Vložím raději originál:' + '\n')
            print(paragraphs[i][1] + '\n')
            generated_text = (paragraphs[i][1] + '\n\n')

        else:
            generated_text = gpt_text

    if gpt_processed == True: #pokud jsme text poslali do GPT, zkontrolujeme rate limits

        t2 = time.time() # nejprve pro čas
        time_between_loops = t2-t
        if time_between_loops < necessary_delay:
            delay = necessary_delay - time_between_loops
            time.sleep(delay)
    

    with open(result_name, 'a', encoding='utf-8') as file: # na závěr smyčky přidá text na konec souboru s výsledkem, postupně tak přidává jednotlivé odstavce
                file.write(generated_text)

print('***HOTOVO***') #je li vše zpracováno, dá nám vědět