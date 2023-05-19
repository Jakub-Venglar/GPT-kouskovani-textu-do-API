import os, openai, json

#todo improvement - dát try/except na openai.error.RateLimitError - počkat a pokračovat od posledního úseku (tzn někde ukládat do slovníku již zpracované nebo počítat odstavce a na začátku přeskočit daný počet odstavců)
#a taky zpomalit posílání

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

openai.api_key = api_key

#max_tokens_per_request = 3500

#funkce, která posílá kousky textu do GPT API

def generate_text_from_paragraphs(paragraph, prompt):
    #prompt += "\n\n" + "\n\n".join(paragraphs)
    
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[{"role": "user", "content": prompt},{"role": "user", "content": paragraph}],
        #max_tokens=max_tokens_per_request,
        temperature=temp,
        n = 1,
        stop=None,
        timeout=5
    )
    message = response['choices'][0]['message']['content']
    return message

#max_tokens_per_paragraph = 850

#načte zdrojový text a rozkouskuje ho po odstavcích (enter na konci řádku)

with open(file_name, 'r', encoding="utf-8") as file:
    text = file.read()

paragraphs = []
for line in text.split("\n"):
    if len(line) > 0:
        paragraphs.append(line)

generated_text = ""

print('Naporcováno a připraveno k magii...' + '\n')

#smyčka, která rozkouskovaný text postupně dávkuje funkci pro zpracování v GPT

for i in range(len(paragraphs)):
    if any(substring in paragraphs[i] for substring in list_to_exclude): #kontroluje, zda v textu je nějaký řetězec, který jej diskvalifikuje z odeslání do GPT
        for substring2 in list_to_exclude:
            if substring2 in paragraphs[i]:
                if include_replacement == True and substring2 in replacements: #pokud máme nastavenou náhradu za takový kousek textu, tak ji aplikuje, jinak dá originální znění
                    inter_text = replacements[substring2] + '\n\n'
                else:
                    inter_text = (paragraphs[i] + '\n\n')
                print(inter_text)
                generated_text = inter_text

    elif len(paragraphs[i])<too_short: #pokud je odstavec moc krátký, GPT by to zmátlo, tak jej jen zkopírujeme
            print('Text je hodně krátký. Vložím raději originál:' + '\n')
            print(paragraphs[i] + '\n\n')
            generated_text = (paragraphs[i] + '\n\n')

    else:
        print('Předávám text do GPT...' + '\n') #předání textu do GPT
        gpt_text = generate_text_from_paragraphs(paragraphs[i], prompt) + '\n\n'
        print('GPT: ' + gpt_text)

        if any(correct_info in gpt_text for correct_info in gpt_annoucements_to_exclude): #pokud GPT vyplivnul nějaké moudro, které máme nastaveno, že nechceme slyšet, tak raději vloží originální text
            print('Vložím raději originál:' + '\n')
            print(paragraphs[i] + '\n')
            generated_text = (paragraphs[i] + '\n\n')

        else:
            generated_text = (gpt_text + '\n\n')

    with open(result_name, 'a', encoding='utf-8') as file: # na závěr smyčky přidá text na konec souboru s výsledkem, postupně tak přidává jednotlivé odstavce
                file.write(generated_text)

print('***HOTOVO***') #je li vše zpracováno, dá nám vědět