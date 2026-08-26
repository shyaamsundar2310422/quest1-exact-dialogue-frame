def test_basic_metadata():
    fps = 23.976
    frame_number = 7798
    timestamp = frame_number / fps

    assert fps > 0
    assert frame_number >= 0
    assert timestamp > 0