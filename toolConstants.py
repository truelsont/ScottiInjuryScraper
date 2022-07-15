programSpiel = """
###############

Team Scotti Injury Webscraper Tool

###############\n
"""

regexForPlayers = ["player", "play", "name"]
import nltk

outputDictTemplate = ({'Name': [], 'Injury':[],'Quote':[],'Date': [], 'Source':[]})

numSearchChunks = 5

class InjuryRecord:
	def __init__(self, playerName, bodyPart, quote, URLsource, date):
		self.playerName = playerName
		self.bodyPart = bodyPart
		self.quote = quote
		self.URLsource = URLsource
		self.date = date

	def __eq__(self, other):
		
		if self.playerName != other.playerName:
			return False
		if self.bodyPart != other.bodyPart:
			return False 

		'''
		if self.date.split("-")[0] == other.date.split("-")[0]:
			q1 = nltk.word_tokenize(self.quote)
			q2 = nltk.word_tokenize(self.quote)
			if [word for word in q1 if word in q2]:
				return True 
			print(q1,q2)
			return False 
		'''
		
		#if self.year == other.year and self.URLsource == other.URLsource:
		#	return True

		#if self.year != other.year or self.sentence == other.sentence:
		#	return True
		
		return True

	def __hash__(self) -> int:
		return self.playerName.__hash__()

	def turnToDict(self):
		dict_data_new  = outputDictTemplate.copy()
		dict_data_new['Name'] = self.playerName
		dict_data_new['Injury'] = self.bodyPart
		dict_data_new['Source'] = self.URLsource
		#dict_data_new['Time Keywords'] = self.length
		dict_data_new['Date'] = self.date
		dict_data_new['Quote'] = self.quote


		return dict_data_new



'''
THis is the list of time words tha will be used to estimate the 
length of the injury

'''
timeWords = ['month','day','week','sunday','monday','tuesday','wednesday','thursday', 'friday', 'saturday', 'sunday']




'''
This is the list of injuries that the program will try to search for


'''
injuryWords = ['abdomen', 'ankle', 'arm', 'back', 'chest', 'ear', 
'elbow', 'eye', 'face', 'finger', 'foot', 'groin', 'hand', 'head', 
'hip', 'jaw', 'knee', 'leg', 'neck', 'pelvis', 'shoulder', 
'stomach', 'thumb', 'toe', 'wrist', 'achilles tendon', 'acl', 'adductor', 
'bicep', 'calf', 'disk', 'fibula', 'flexor', 'forearm', 'hamate', 'hamstring', 
'heel', 'index', 'labrum', 'lateral', 'lower', 'mcl', 'meniscus', 'middle', 
'oblique', 'patella', 'pectoral', 'pinky', 'quad', 'radius', 'rib cage', 
'ring', 'rotator cuff', 'tibia', 'tricep', 'ucl', 'ulna', 'unspecified',
'abrasion', 'affective disorder', 'aneurysm', 'appendicitis', 
'arterial defect', 'arthritic', 'avulsion', 'blister', 'blood clot', 
'bone chip', 'bone spur', 'bruise', 'bulging', 'bunion', 'bursitis', 
'calcium deposit', 'capsulitis', 'cardiac', 'cartilage damage', 
'circulatory condition', 'concussion', 'cyst', 'derangement', 
'detached', 'dislocated', 'dizziness', 'fracture', 'fractured metacarpal', 
'glaucoma', 'hematoma', 'hernia', 'herniated', 'hyperextension', 'illness', 
'impingement', 'infection', 'inflammation', 'instability', 
'irritation', 'kidney stone', 'laceration', 'lesion', 'loose bodies', 
'medial epicondylitis', 'nerve damage', 'nerve irritation', 'neuritis', 
'numbness', 'pain', 'pinched nerve', 'plantar fascitis', 'rupture', 
'ruptured tendon', 'scratched cornea', 'separated', 'shin splints', 'sinus',
'slap lesion', 'sore ', 'spasms', 'spinal stenosis', 'staph infection', 
'stiffness', 'strain ', 'stress', 'subluxation', 'surgery', 'synovitis',
'tear', 'tendonitis', 'tenosyvitis', 'vascular constriction', 'vertigo', 
'wart', 'weakness', 'sprain', 'torn','ejected','body','tightness']





