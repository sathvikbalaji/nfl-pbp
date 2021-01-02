import uuid

def random_eight_character_id():
	return uuid.uuid4().hex[:8]