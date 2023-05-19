# GPT-kouskovani-textu-do-API
Script, který naporcuje dodaný text po odstavcích (resp.dělí přes /n) a posílá ho do GPT přes OpenAI API.
Potřebujete API key, který najdete ve svém OpenAI účtu.
V první verzi bez kontroly, zda je počet tokenů ok. Většina běžných odstavců vyhovuje.

# Co obsahuje nastavení:
- temperature: Hodnota, která GPT říká, jak moc být "kreativní". Pro korektury se nám osvědčilo 0.5. Může být 0 (velmi deterministické chování) - 2 (velmi volné chování)
- apiKey: vaše OpenAi API key
- modelEngine: jaká konkrétní verze GPT se použije. gpt-3.5-turbo je doporučována pro poměr cena/výkon.
- input a result name: Jméno souboru na vstupu (kam jste uložili data pro zpracování) a výstupu.
- listToExclude: Pokud v odstavci najde daný řetězec, ani ho nepošle do GPT (aby ji nemátl) a jen ho zkopíruje.
- gptExclude: Můžete si ladit. Pokud vám robot pravidelně vrací nějakou hlášku, protože ho určitá část textu zmátla (např. "Text je gramaticky správný, není potřeba dělat korekturu"), přidejte ji sem a opět se do výsledku vloží původní odstavec.
- prompt: Příkaz, který se odešle spolu s textem. Může to být např. "Udělej gramatickou korekturu textu. Nepřidávej nic, co už v textu není." nebo "Přelož tento text do angličtiny." atp.
- includeReplacement: Pokud pravda, tak vám script pomůže rovnou nahradit odstavce s určitými výrazy něčím, co chcete. Například kódem, jménem atp. Zadává se formou "slovníku" - vize příklad.
- tooShort: Počet znaků, pod které je odstavec ignorován a opět rovnou přepsán, jak je. Použito, protože GPT má problém s krátkými větičkami nebo jednotlivými slovy a často diskutuje o smysluplnosti příkazu nad nimi :)

# Jak používat
- Po stažení smažte z názvů souborů settings a krmení " - example" a doplňte svá data a nastavení.
- do setting vložte váš API key
- Spusťe script a počkejte si na výsledek.
- Zpracované odstavce jsou postupně přidávány do souboru s názvem podle nastavení. Tzn. pokud vám script z jakéhokoliv důvodu spadne, po znovuspuštění bude zase přidávat data na konec souboru (ale zpracování pojede od začátku - ošetření tohoto bude v nějaké další verzi). 
