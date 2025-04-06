import pytest
from verification import IDVerification

@pytest.fixture
def id_verification():
    return IDVerification()

def test_verify_ajinkya(id_verification):
    img_ref = "server/verification/testing/ajay2.jpeg"
    face_ref = "server/verification/testing/ajay1.jpeg"
    first_name = "Ajinkya"
    last_name = "Gokule"
    
    result = id_verification.verify(img_ref, face_ref, first_name, last_name)
    assert result is not None
    assert result['id_res']['verified'] is True
    assert result['face_res']['verified'] is True

def test_verify_colin(id_verification):
    img_ref = "server/verification/testing/colin2.jpeg"
    face_ref = "server/verification/testing/colin1.jpeg"
    first_name = "Colin"
    last_name = "Pannikkat"
    
    result = id_verification.verify(img_ref, face_ref, first_name, last_name)
    assert result is not None
    assert result['id_res']['verified'] is True
    assert result['face_res']['verified'] is True

def test_verify_david(id_verification):
    img_ref = "server/verification/testing/david2.jpeg"
    face_ref = "server/verification/testing/david1.jpeg"
    first_name = "David"
    last_name = "Gesl"
    
    result = id_verification.verify(img_ref, face_ref, first_name, last_name)
    print(result)
    assert result is not None
    assert result['id_res']['verified'] is True
    assert result['face_res']['verified'] is True

def test_verify_invalid(id_verification):
    img_ref = "server/verification/testing/napkin.jpeg"
    face_ref = "server/verification/testing/ajay1.jpeg"
    first_name = "Invalid"
    last_name = "Person"
    
    result = id_verification.verify(img_ref, face_ref, first_name, last_name)
    assert result is None