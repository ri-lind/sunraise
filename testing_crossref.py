from crossref.restful import Works, Etiquette
import json

my_ettiquete = Etiquette('Sunrise Prototype', '1.0', 'N/A', 'r.harizaj@uni-muenster.de')

works = Works(etiquette=my_ettiquete)


ai_works = works.query("AI").query("Academia").query("Industry").filter(has_abstract="true").sort("issued")


with open("research_articles", "w") as research:
    ai = ai_works.sample(10)
    
    for i in ai:
        research.write(f"\"{i.get("title")}\", \"{i.get("abstract")}\", {i.get("issued")}")
        research.write("\n")