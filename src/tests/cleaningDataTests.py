import pytest
import json
from io import StringIO
import os,sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DataAnalysis.APIDataHandler import APIDataHandler


def test01_removeMissingorNullValues(monkeypatch):
    '''
    Test case to check if the function removes the records with missing or null values
    And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

    Test01: 
    Entity where the role is None, should be removed 
    '''
   
    mock_json_data = json.dumps([
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": None},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
    ])

    def mock_open(*args, **kwargs):
        return StringIO(mock_json_data)

    monkeypatch.setattr('builtins.open', mock_open)

    handler = APIDataHandler("http://localhost:8002/employees")

    result = handler.removeMissingorNullValues()

    expected_output = [
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
    ]
    assert result == expected_output

def test02_removeMissingorNullValues(monkeypatch):
    '''
    Test case to check if the function removes the records with missing or null values
    And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

    Test02: 
    Entity where the role is "", should be removed
    '''
    
    mock_json_data = json.dumps([
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": ""},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
    ])

    def mock_open(*args, **kwargs):
        return StringIO(mock_json_data)

    monkeypatch.setattr('builtins.open', mock_open)

    handler = APIDataHandler("http://localhost:8002/employees")

    result = handler.removeMissingorNullValues()

    expected_output = [
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
    ]
    assert result == expected_output

def test03_removeMissingorNullValues(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test03: 
        Entity where a field is missing but not in the list of fields which removes the whole entity, nothing happens
        '''
        
        mock_json_data = json.dumps([
            {"lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeMissingorNullValues()
    
        expected_output = [
            {"lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ]
        assert result == expected_output

def test04_removeMissingorNullValues(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test04: 
        Entity where a field is missing but not in the list of fields which removes the whole entity and the role is "" -> whole record should be removed
        '''
        mock_json_data = json.dumps([
            {"lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": ""},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeMissingorNullValues()
    
        expected_output = [
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ]
        assert result == expected_output

def test05_removeMissingorNullValues(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test05: 
        Entity where a field is missing but not in the list of fields which removes the whole entity and the role is None -> whole record should be removed
        '''
        mock_json_data = json.dumps([
            {"lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": None},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeMissingorNullValues()
    
        expected_output = [
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ]
        assert result == expected_output

def test06_removeMissingorNullValues(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test06: 
        Different entities with different missing values first one the firstname and the role is "", third one the role is None -> both should be removed 
        '''
        mock_json_data = json.dumps([
            {"lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": ""},
            {"firstname": "Hans", "": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "None"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": None},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeMissingorNullValues()
    
        expected_output = [
            {"firstname": "Hans",  "password": "1234", "email": "hans.franz@gmail.com", "role": "None"},
            {"firstname": "Hans", "lastname": "Franz" , "password" : "1234" ,"email": "hans.franz@gmail.com", "role": "admin"}
        ]
        assert result == expected_output

def test07_removeMissingorNullValues(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test07: 
        Entity where the key is "" -> field should be removed
        '''
        mock_json_data = json.dumps([
            {"": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "None"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeMissingorNullValues()
    
        expected_output = [
            {"password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz" , "password" : "1234" ,"email": "hans.franz@gmail.com", "role": "None"},
            {"firstname": "Hans", "lastname": "Franz" , "password" : "1234" ,"email": "hans.franz@gmail.com", "role": "admin"}
        ]
        assert result == expected_output

def test08_handleCaseSensitivity(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test08: 
        Case where the case sensitivity should be handled -> all str values should be lowercased
        '''
        mock_json_data = json.dumps([
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "Admin"},
            {"firstname": "Hans", "lastname": "Franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "ADMIN"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.handleCaseSensitivity()
    
        expected_output = [
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
        ]
        assert result == expected_output

def test09_handleCaseSensitivity(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test09: 
        Case where the case sensitivity should be handled, but no case insensitives are present -> nothing should be changed
        '''
        mock_json_data = json.dumps([
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.handleCaseSensitivity()
    
        expected_output = [
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"},
            {"firstname": "hans", "lastname": "franz", "password": "1234", "email": "hans.franz@gmail.com", "role": "admin"}
        ]
        assert result == expected_output


def test10_removeDuplicates(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test10: 
        Case where duplicates are present, one should be removed
        '''
        mock_json_data = json.dumps([
            {"customerId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeDuplicates()
    
        expected_output = [
            
            {"customerId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ]
        assert result == expected_output
    
def test11_removeDuplicates(monkeypatch): 
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test11: 
        Case where no duplicates are present, zero should be removed
        '''
        mock_json_data = json.dumps([
            {"customerId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12346,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeDuplicates()
    
        expected_output = [
            
            {"customerId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12346,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ]
        assert result == expected_output

def test12_removeDuplicates(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test12: 
        Case where no duplicates are present, but keys are different, zero should be removed
        '''
        mock_json_data = json.dumps([
            {"customersId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12346,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeDuplicates()
    
        expected_output = [
            
            {"customersId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12346,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ]
        assert result == expected_output

def test13_removeAllWhitespaces(monkeypatch):
        '''
        Test case to check if the function removes the records with missing or null values
        And checks if the data contains data which could mislead in the analysis (Defined in REMOVINGS.py)

        Test13: 
        Case where whitespaces are present, whitespaces should be remove
        '''
        mock_json_data = json.dumps([
            {"customersId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "Jo hn","lastname": "D oe","companyNumber": "COMP 123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12346,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "Jo hn","lastname": "Do e","companyNumber": "COMP 123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ])
    
        def mock_open(*args, **kwargs):
            return StringIO(mock_json_data)
    
        monkeypatch.setattr('builtins.open', mock_open)
    
        handler = APIDataHandler("http://localhost:8002/employees")
    
        result = handler.removeAllWhitespaces()
    
        expected_output = [
            
            {"customersId": 12345,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
            {"customerId": 12346,"email": "example@example.com","phoneNumber": "+1234567890","addressId": 6789,"password": "encrypted_password_here","firstname": "John","lastname": "Doe","companyNumber": "COMP123456","role": "admin","signedUp": "2024-01-01T12:34:56Z","businessSector": "technology"},
        ]
        assert result == expected_output
      
    
      
        