# LangGraph - Unittests

IL testing è una parte cruciale per ogni applicazione e il design di LangGraph fornisce un modo intutitivo per implementare unittests per i nostri agenti.

In questo modo ci assicuriamo che i nostri agenti siano robusti, affidfabili e che siano in grado di gestire casi limite.

## Unittest

Unittest è progettato per validare unità individuali della funzionalità in maniera isolata. Nel consteso di LangGraph, una unità corrisponde a un singolo nodo all'interno del grafo, dato che ciascun nodo è una funzione indipendente.

Dunque, il nostro obiettivo è testare ciascun nodo separatamente, garantendo che esso si comporti correttamente dati degli input specifici.

Concentrandosi sui nodi come unità isolate, possiamo assicurare affidabili funzionalità, mentre manteniamo i test veloci e indipendenti da dipendeze esterne.