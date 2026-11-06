"""Response shapes for the Sandbox column dictionary."""

from pydantic import BaseModel, Field

DATA_NOTE = (
    "Definitions from the PDP data dictionaries and the mock data's column lookup. The shared mock "
    "data is synthetic: nothing built on it is a finding about real students or institutions."
)


class DictionaryValue(BaseModel):
    """One code as the data dictionary writes it, and what it means."""

    code: str
    meaning: str | None = Field(
        description="Null where the dictionary lists the code without a meaning."
    )


class ColumnSource(BaseModel):
    """One raw file column that fills the normalized column."""

    source_file: str = Field(description="Such as pdp_cohort_data.csv, in data/raw/.")
    source_column: str = Field(description="The column name as the file writes it.")
    dictionary_file: str | None = Field(
        description="The markdown dictionary with the full entry. Null if the dictionary has none."
    )
    lookup_description: str | None = Field(
        description="From data/dictionaries/column_lookup.csv, with the mock-data specifics."
    )


class StoredColumn(BaseModel):
    """How the model stores the column, from destination_schema.yaml."""

    type: str
    nullable: bool
    unknown_value: str | None = Field(description="Stored when the source says it doesn't know.")
    allowed_values: list[str] | None = Field(
        description="Stored codes the schema's rules allow. Can differ from the dictionary's."
    )


class ColumnDefinition(BaseModel):
    """What one normalized column means, and how it's stored."""

    table: str
    column: str
    dictionary_name: str | None = Field(
        description="The data dictionary's name. Null if it has no entry."
    )
    description_source: str | None = Field(
        description="The source file whose dictionary entry gives the description and codes."
    )
    description: str | None
    dictionary_values: list[DictionaryValue] = Field(
        description="The dictionary's codes as it writes them. Stored codes: stored.allowed_values."
    )
    notes: str | None = Field(
        description="Markdown: the entry's notes, such as **Note:** or Also includes."
    )
    sources: list[ColumnSource]
    stored: StoredColumn


class ColumnDefinitionList(BaseModel):
    """Every column definition that matched the filters, in the schema's table and column order."""

    columns: list[ColumnDefinition]
    note: str = DATA_NOTE
