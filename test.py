import botocove

@botocove.cove()
def test(session):
    return session.client("sts").get_caller_identity()

print(test())

