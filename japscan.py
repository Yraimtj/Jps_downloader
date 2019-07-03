import time
import sys
import os
try:
	import bs4 as bs
	import cloudscraper
	from PIL import Image
except Exception as e:
	print("ERROR IMPORT")
	print(e)
	os.system("pause")

def main():
	while True:
		print("1. Japscan - chapitre/volume automatique")
		print("2. Japscan - volume")
		print("3. Japscan - chapitre")
		print("4. Japscan - url (pour faire des tests) ")
		choix_site = input("Que voulez-vous faire  ? ")

		if choix_site in ["1","2","3","4"]:
			break 
		else:
			print("Erreur")
			time.sleep(1.5)


	if choix_site == "4":
		url = input("Entrez l'url : ")
		scraper = cloudscraper.create_scraper()
		code_source = scraper.get(url, stream=True)

		img = Image.open(code_source.raw)
		img.save('test.png')
		print(f"Image sauvegardée sous le nom : test.png")
		os.system("pause")
		sys.exit(0)


	if choix_site == "1":
		chap_vol = "auto"
	elif choix_site == "2":
		chap_vol = "vol"
	elif choix_site == "3":
		chap_vol = "chap"


	nom_manga = input("Entrez le nom du manga : ")
	chap = input("Entrez le numéro du chapitre/volume (si il y a plusieurs chapitre, séparez les par une virgule) : ")
	
	chap = chap.split(",")
	if len(chap) == 2:
		chap_min = chap[0]
		chap_max = chap[1]
	else:
		chap_min = chap[0]
		chap_max = chap[0]

	for chapitre in range(int(chap_min),int(chap_max) + 1):
		jap = Japscan()
		jap.telecharger(nom_manga,chapitre,chap_vol)
		print("Tous les chapitres ont été téléchargé")
	##




class Japscan():
	def __init__(self):
		self.session = cloudscraper.create_scraper()


	def telecharger(self, manga, chapitre, chap_vol="auto"): # chap_vol = chap / vol / auto


		self.url_base_chapitre = f"https://www.japscan.to/lecture-en-ligne/{manga}/{chapitre}/1.html"
		self.url_base_volume = f"https://www.japscan.to/lecture-en-ligne/{manga}/volume-{chapitre}/1.html"

		if chap_vol == "chap":
			liste_url = [self.url_base_chapitre]
		elif chap_vol == "vol":
			liste_url = [self.url_base_volume]
		elif chap_vol == "auto":
			liste_url = [self.url_base_chapitre, self.url_base_volume]

		for url in liste_url:
			images = {}

			code_source = self.session.get(url)
			print("Code source récupéré")

			soup = bs.BeautifulSoup(code_source.content, "html.parser")

			h2_all = soup.findAll('h2')
			for h2 in h2_all:
				if h2.text == "Cette page n'existe pas ou plus":
					if chap_vol != "auto":
						print("ERREUR, CETTE PAGE N'EXISTE PAS !!!")
						os.system("pause")
						sys.exit(0)

			#
			# Récupérer le format de https://c.japscan.to/lel/One-Piece/936/04.jpg
			base_url_img = "https://c.japscan.to/lel/"
			img_1 = soup.find('div',attrs={"id":u"image"})
			img_1_url = img_1["data-src"]
			manga = "".join(img_1_url.split("/")[-3])
			modele_url_img = base_url_img + manga
			#

			pages_vrac = soup.find('select',attrs={"id":u"pages"})
			pages_brut = pages_vrac.findAll('option')
			for page in pages_brut:
				page_data_img = page["data-img"]
				page_titre = page.text.split(" ")[1]
				page_url = page["value"]

				chapitre = page_url.split("/")[-2]
				if chapitre[:5] == "volum":
					chapitre = "V" + chapitre[1:]
				url_image = modele_url_img + "/" + chapitre + "/" + page_data_img

				images[page_titre] = url_image

			#images = {'01': 'https://c.japscan.to/lel/One-Piece/936/01.jpg', '02': 'https://c.japscan.to/lel/One-Piece/936/04.jpg', '03': 'https://c.japscan.to/lel/One-Piece/936/05.jpg', '04': 'https://c.japscan.to/lel/One-Piece/936/06.jpg', '05': 'https://c.japscan.to/lel/One-Piece/936/07.jpg', '06': 'https://c.japscan.to/lel/One-Piece/936/08.jpg', '07': 'https://c.japscan.to/lel/One-Piece/936/09.jpg', '08': 'https://c.japscan.to/lel/One-Piece/936/10.jpg', '09': 'https://c.japscan.to/lel/One-Piece/936/11.jpg', '10': 'https://c.japscan.to/lel/One-Piece/936/12.jpg', '11': 'https://c.japscan.to/lel/One-Piece/936/13.jpg', '12': 'https://c.japscan.to/lel/One-Piece/936/14.jpg', '13': 'https://c.japscan.to/lel/One-Piece/936/15.jpg', '14': 'https://c.japscan.to/lel/One-Piece/936/16.jpg', '15': 'https://c.japscan.to/lel/One-Piece/936/17.jpg', '16': 'https://c.japscan.to/lel/One-Piece/936/18.jpg', '17': 'https://c.japscan.to/lel/One-Piece/936/19.jpg'}

			for nom_img, url_img in images.items():
				# print(nom_img, url_img)

				os.makedirs(f"final/{manga}/{chapitre}", exist_ok=True)

				requete_img = self.session.get(url_img, stream=True)
				img = Image.open(requete_img.raw)
				nom = f"final/{manga}/{chapitre}/{nom_img}.png"
				img.save(nom)

				print(f"{nom}")

		return "Success"


if __name__ == '__main__':
	main()
