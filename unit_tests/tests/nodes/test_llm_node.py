from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage

from unit_tests.code_to_test import llm_node


@patch("unit_tests.code_to_test.create_llm")
@pytest.mark.asyncio

# questa funzione non verrà veramente chiamata, ma usiamo mock return_value
async def test_llm_node(mock_create_llm, state):

    """
    Test the async llm_node frunction with a mocked LLM.
    """
    # llm fake con risultato fake
    mock_llm = AsyncMock()

    mock_response = AsyncMock()

    mock_response.content = "Mocked AI response"
    mock_llm.ainvoke.return_value = mock_response

    mock_create_llm.return_value = mock_llm

    # creiamo il prompt fake da passare all'llm

    mock_prompt = MagicMock()
    mock_prompt.messages = state["messages"]

    state["prompt"] = mock_prompt

    # chiamiamo effettivamente il nodo llm_node
    updated_state = await llm_node(state)

    # controlliamo se answer nello updated_state è "Mocked AI response"
    assert updated_state["answer"] == "Mocked AI response"
    assert updated_state["messages"][-1] == AIMessage(content="Mocked AI response")
    # vogliamo anche controllare se il metodo .ainvoke è chiamato una sola volta
    # con tutti i messaggi dallo stato
    mock_llm.ainvoke.assert_called_once_with(state["messages"])
    # vogliamo vedere se mock_create_llm è stata chiamata una sola volta
    mock_create_llm.assert_called_once()



