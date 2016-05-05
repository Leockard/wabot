# test.py
# just playin' around withe the W|A api

import zulip
import wolframalpha as WA


BOT_EMAIL = "wa-bot@zulip.com"
ZULIP_KEY = "uBC18mEEmGqy7K35YpICSLAkRmYmWwEV"
ADDRESS   = "http://localhost:9991"
WA_KEY    = "EE7XKT-H97T699E6A"



class WAbot():

    mention_str = "@**wabot**"
    

    def __init__(self):
        # Connect to both services
        print("Connecting...")
        self.client = zulip.Client(email=BOT_EMAIL, api_key=ZULIP_KEY, site=ADDRESS)
        self.subscribe_all()
        self.alpha = WA.Client(WA_KEY)


    def subscribe_all(self):
        self.client.add_subscriptions([{"name": s["name"] for s in self.client.get_streams()["streams"]}])


    def listen(self):
        # This is a blocking call that will run forever.
        self.client.call_on_each_message(lambda msg: self.respond(msg) if self.valid_msg(msg) else None)


    def valid_msg(self, msg):
        return self.mention_str in msg["content"]


    def get_query(self, msg):
        # Everything after the @wabot call is considered to be the query
        beg = msg["content"].index(self.mention_str) + len(self.mention_str)
        return msg["content"][beg:].strip(" ,")


    def valid_result(self, res):
        return len(res.pods) > 0


    def announce_query(self, msg):
        self.client.send_message(self.create_reply(msg, "Beep Beep Boop..."))


    def post_result(self, msg, res):
        self.client.send_message(self.create_reply(msg, next(res.results).text))


    def post_invalid_query(self, msg, res):
        self.client.send_message(self.create_reply(msg, "DOES NOT COMPUTE."))

        
    def create_reply(self, msg, body):
        return {
            "type": msg["type"],
            "to": msg["display_recipient"],
            "subject": msg["subject"],
            "content": body
            }


    def respond(self, msg):
        self.announce_query(msg)
        
        res = self.alpha.query(self.get_query(msg))
        
        if self.valid_result(res):
            print("Posting response...")
            self.post_result(msg, res)
        else:
            print("Posting invalid query...")
            self.post_invalid_query(msg, res)



if __name__ == "__main__":
    wabot = WAbot()

    print("Listening...")
    wabot.listen()
