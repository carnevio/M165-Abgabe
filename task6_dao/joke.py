class Joke:
    def __init__(self, text, category=None, author=""):
        """
        Klasse fuer einen Witz. (Aufgabe 6.2.1)
        """
        self.text = text
        self.category = category if category is not None else []
        self.author = author

    def to_document(self):
        """
        Konvertiert das Witz-Objekt in ein MongoDB-Dokument.
        """
        return {
            "text": self.text,
            "category": self.category,
            "author": self.author,
        }

    @classmethod
    def from_document(cls, document):
        """
        Erstellt ein Witz-Objekt aus einem MongoDB-Dokument.
        """
        categories = document.get("category", [])
        if not isinstance(categories, list):
            categories = [str(categories)]

        return cls(
            text=str(document.get("text", "")),
            category=[str(item) for item in categories],
            author=str(document.get("author", "")),
        )

