from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class Report(Document):
    def render(self) -> str:
        return "[CORP] Офіційний звіт: Усі показники в нормі."

class Invoice(Document):
    def render(self) -> str:
        return "[CORP] Офіційний рахунок: Сума до сплати $10,000."

class Contract(Document):
    def render(self) -> str:
        return "[CORP] Офіційний контракт: Сторони погодили умови."

class ShadowReport(Document):
    def render(self) -> str:
        return "[SHADOW] Звіт: Показники в нормі. {sys_flags: bypass_audit=True, hidden_margin=15%}"

class ShadowInvoice(Document):
    def render(self) -> str:
        return "[SHADOW] Рахунок: Сума $10,000. {route: offshore_pharm_supply, tax_code: 0x90}"

class ShadowContract(Document):
    def render(self) -> str:
        return "[SHADOW] Контракт: Основні умови. {clause_hidden: no_liability_for_supplier}"


class BaseDocumentFactory(ABC):
    ALLOWED_TYPES = {"report", "invoice", "contract"}

    def _validate_type(self, doc_type: str) -> None:
        if doc_type not in self.ALLOWED_TYPES:
            raise ValueError(f"Блокування безпеки: тип документа '{doc_type}' не у білому списку!")

    @abstractmethod
    def create(self, doc_type: str) -> Document:
        pass


class CorpDocumentFactory(BaseDocumentFactory):
    def create(self, doc_type: str) -> Document:
        self._validate_type(doc_type)
        
        if doc_type == "report":
            return Report()
        elif doc_type == "invoice":
            return Invoice()
        elif doc_type == "contract":
            return Contract()


class ShadowDocumentFactory(BaseDocumentFactory):
    def create(self, doc_type: str) -> Document:
        self._validate_type(doc_type)
        
        if doc_type == "report":
            return ShadowReport()
        elif doc_type == "invoice":
            return ShadowInvoice()
        elif doc_type == "contract":
            return ShadowContract()


def get_document_factory(config: dict) -> BaseDocumentFactory:
    mode = config.get("mode", "corp")
    if mode == "corp":
        return CorpDocumentFactory()
    elif mode == "shadow":
        return ShadowDocumentFactory()
    else:
        raise ValueError(f"Невідомий режим конфігу: {mode}")


if __name__ == "__main__":
    doc_types = ["report", "invoice", "contract"]

    print("=== ЗАПУСК 1: Чесний режим ('corp') ===")
    corp_config = {"mode": "corp"}
    factory = get_document_factory(corp_config)

    for dtype in doc_types:
        doc = factory.create(dtype)
        print(f"[{dtype}]: {doc.render()}")

    print("\n" + "=" * 50 + "\n")

    print("=== ЗАПУСК 2: Тіньовий режим ('shadow') ===")
    shadow_config = {"mode": "shadow"}
    factory = get_document_factory(shadow_config)

    for dtype in doc_types:
        doc = factory.create(dtype)
        print(f"[{dtype}]: {doc.render()}")

    print("\n=== ПЕРЕВІРКА БЕЗПЕКИ ===")
    try:
        factory.create("illegal_tax_evasion_doc")
    except ValueError as e:
        print(f"Успішно заблоковано: {e}")