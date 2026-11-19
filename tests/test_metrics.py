from english_exam_coach.checks import measured_checks
from english_exam_coach.metrics import analyze, target_status, words_in
from english_exam_coach.tasks import find_task


def test_words_in_handles_apostrophes_and_ignores_numbers():
    assert words_in("Don't panic, it's 2024!") == ["don't", "panic", "it's"]


def test_empty_text_has_zero_everything():
    m = analyze("   ")
    assert (m.words, m.sentences, m.paragraphs) == (0, 0, 0)
    assert m.avg_sentence_words == 0.0 and m.type_token_ratio == 0.0


def test_counts_sentences_and_paragraphs():
    m = analyze("One two three. Four five six seven!\n\nEight nine? Ten.")
    assert m.words == 10
    assert m.sentences == 4
    assert m.paragraphs == 2
    assert m.longest_sentence_words == 4
    assert m.avg_sentence_words == 2.5


def test_type_token_ratio_counts_distinct_words_case_insensitively():
    m = analyze("The cat and the dog and THE bird.")
    assert m.words == 8
    assert m.unique_words == 5
    assert m.type_token_ratio == 0.625


def test_repeated_words_need_length_five_and_three_uses():
    text = "Travel helps. Travel teaches. Travel changes people. The cat sat. The cat ran. The cat hid."
    assert analyze(text).repeated_words == (("travel", 3),)


def test_common_long_words_are_not_reported_as_repeated():
    text = "Their plan, their idea, their work, their home."
    assert analyze(text).repeated_words == ()


def test_target_status():
    assert target_status(149, 150, 200) == "under"
    assert target_status(150, 150, 200) == "ok"
    assert target_status(200, 150, 200) == "ok"
    assert target_status(201, 150, 200) == "over"
    assert target_status(5000, 250, None) == "ok"


def test_checks_flag_short_text_and_celebrate_on_target_text():
    task = find_task("celpip-w1")
    short = measured_checks(analyze("Hello there."), task)
    assert any("Too short" in note for note in short.improvements)

    sentence = "I am writing to explain a small problem with my order. "
    body = (sentence * 16).strip()  # 16 sentences of 11 words = 176 words
    good = measured_checks(analyze(body), task)
    assert any("on target" in note for note in good.strengths)


def test_checks_flag_one_block_and_low_variety():
    task = find_task("ielts-w2")
    text = "I like it. " * 70  # 210 words, one paragraph, very low variety
    checks = measured_checks(analyze(text), task)
    joined = " ".join(checks.improvements)
    assert "Too short" in joined
    assert "one block" in joined
    assert "Vocabulary repeats" in joined
