"""
Utilizziamo delle simulazioni per testare
quindi creiamo un Mock vector database il quale è il db object

Questo per assicuaraci che la funzione retrieve_node() sia testata isolatamente 
con in puts e outputs controllati.

@patch() è un decoratore fornito dal modulo unittest.mock di Python. Viene usato per mockare (sostituire temporaneamente) oggetti, 
funzioni o metodi durante i test unitari. Questo è utile per testare il comportamento di un componente senza eseguire effettivamente parti del codice 
che potrebbero avere effetti collaterali (ad esempio chiamate a database, API, file system, ecc.).
"""

import pytest

from unit_tests.code_to_test import retrieve_node

@patch("unit_tests.code_to_test.retrieve_node")
@patch("unit_tests.code_to_test.db")
@pytest.mark.asyncio
async def test_retrieve_node(mock_db, mock_create_retriever, state):
    """
    Test the async retrieve_node function with mocked dependencies.
    """

    mock_retriever = AsyncMock()
    mock_retriever.ainvoke.return_value = [
        {"title": "Document 1", "content": "Content of Document 1"},
        {"title": "Documents 2", "content": "Content of Document 2"}
    ]

    mock_create_retriever.return_value = mock_retriever
    updated_state = await retrieve_node(state)
 

    # vogliamo sapere se l'updated_state è come ci aspettiamo 
    assert updated_state["context"] == [
        {"title": "Document 1", "content": "Content of Document 1"},    
        {"title": "Documents 2", "content": "Content of Document 2"}
    ]

    # chiamiamo il fake db come retriever 
    mock_create_retriever.assert_called_once_with(mock_db, k=2)

    # testiamo se .ainvoke() del nostro fake retriever con l'input corretto
    mock_retriever.ainvoke.assert_called_once_with(state["question"])
