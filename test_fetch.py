from fetch import score_pay

def test_score_pay_high_salary():
    # Arrange: a made-up job paying $130,000 a year
    record = {"pay_max": 120000, "pay_interval": "PA"}

    # Act: score it
    score = score_pay(record)

    # Assert: check the points
    assert score == 10

def test_score_no_pay():
    #Arrange: if job has no pay
    record = {"pay_max": None, "pay_interval": None}

    # Act: score it
    score = score_pay(record)

    #Assert: check the points
    assert score == 5
