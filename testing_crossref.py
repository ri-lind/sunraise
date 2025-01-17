from crossref.restful import Works, Etiquette
my_ettiquete = Etiquette('Sunrise Prototype', '1.0', 'N/A', 'r.harizaj@uni-muenster.de')

works = Works(etiquette=my_ettiquete)


ai_works = works.query("AI Academia Industry")
ai_works = ai_works.filter(has_abstract="true")
ai_works = ai_works.sort("issued")

sample_works = ai_works.sample(5)

print(sample_works.count)