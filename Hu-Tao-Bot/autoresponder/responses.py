import random

def get_response(text):
    triggers = [(gm_triggers, gm_responses), 
                (gn_triggers, gn_responses), 
                (good_afternoon_triggers, good_afternoon_responses), 
                (good_evening_triggers, good_evening_responses), 
                (hbd_triggers, hbd_responses)]

    for content in triggers:
        if text.startswith(tuple(content[0])):
            return random.choice(content[1])

    return ""

gm_triggers = ["good mornin", "gm", "mornin", "gud mornin"] 

gm_responses = ["Good morning!",
                "Good morning! Glad to see you aren't in a coffin today, if you ever need one you know where to look!",
                "Well are those who rise in the early morn, while those late to bed I shall forewarn~",
                "Good morning! Death is inevitable, but don't worry, we’re doing a 50% coffin discount today!",
                "Good morning! Today is another day closer to another coffin purchase.",
                "Good morning! Wanna come over for tea?",
                "Good morning! I wonder how many clients we will have today."]

gn_triggers = ["good night", "gn", "gud night"] 

gn_responses = ["Oh, you sleepy? Get some rest, I'm gonna take a walk by myself",
                "Good night!",
                "Good night, those late to bed I shall forewarn",
                "Good night! Would you like a coffin to sleep in?",
                "Good night! See you on the other side!",
                "You scared yet?",
                "Run around all you like during the day, but you should be careful during the night. When I'm not around, best keep your wits about you."]

good_afternoon_triggers = ["good afternoon"]

good_afternoon_responses = ["Yo! Afternoon! Had lunch?",
                            "Good afternoon!",
                            "Good afternoon! The day sure is going by quick",
                            "Good afternoon! Would you like a coffin?",
                            "Good afternoon! Wanna come over for tea?"]

good_evening_triggers = ["good evening"]

good_evening_responses = ["Hee-hee, moon's out, and so am I!",
                          "Good evening!",
                          "Good evening! Would you like a coffin?",
                          "Good evening! Do you like to star gaze?",
                          "Good evening! Do you think the stars are our ancestors?",
                          "Good evening! Are you watching the sunset?"]

hbd_triggers = ["hbd", "happy birthday", "happy bday"]

hbd_responses = ["Tonight the stars are dazzling and the moon majestic, it must be a special day... But just what day could it be... Haha, I know, I know! It's your birthday! It really is a great day.",
                 "Happy birthday!"
                 "Happy birthday! Would you like a coffin?"
                 "Happy birthday! We offer birthday discounts on our coffins, would you like one?",
                 "Happy birthday! You're one year closer to using a coffin hehe",
                 "Happy birthday! Would you like me to help you cross over?",
                 "Happy birthday! I wonder how many you have left"]