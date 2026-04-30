from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, validator


class FieldType(str, Enum):
    """Supported field types."""
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    EMAIL = "email"
    DATE = "date"
    DATETIME = "datetime"
    PHONE = "phone"
    JSON = "json"


class AuthRole(str, Enum):
    """Auth roles in the system."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    PREMIUM_USER = "premium_user"


class HTTPMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class Entity(BaseModel):
    """Database entity definition."""
    name: str = Field(..., description="Entity name (singular, PascalCase)")
    plural: str = Field(..., description="Plural form")
    description: str = Field(..., description="What this entity represents")
    fields: dict[str, "SchemaField"] = Field(..., description="Field definitions")
    
    @validator("name")
    def validate_entity_name(cls, v):
        if not v or not v[0].isupper():
            raise ValueError("Entity name must be PascalCase (e.g., User, Contact)")
        return v


class SchemaField(BaseModel):
    """Entity field definition."""
    name: str = Field(..., description="Field name (snake_case)")
    type: FieldType = Field(..., description="Field type")
    required: bool = Field(default=True, description="Is field required?")
    unique: bool = Field(default=False, description="Is field unique?")
    indexed: bool = Field(default=False, description="Should field be indexed?")
    description: str = Field(default="", description="Field description")
    
    @validator("name")
    def validate_field_name(cls, v):
        if not v.islower() and "_" not in v:
            raise ValueError("Field name must be snake_case")
        return v


class DBSchema(BaseModel):
    """Database schema definition."""
    entities: dict[str, Entity] = Field(..., description="Map of entity_name -> Entity")
    relations: list["Relation"] = Field(default_factory=list, description="Foreign key relations")
    
    def get_entity(self, name: str) -> Optional[Entity]:
        return self.entities.get(name)


class Relation(BaseModel):
    """Relationship between entities."""
    from_entity: str = Field(..., description="Source entity")
    to_entity: str = Field(..., description="Target entity")
    relation_type: str = Field(..., description="one_to_one, one_to_many, many_to_many")
    foreign_key: str = Field(..., description="Foreign key field name")


class UIComponent(BaseModel):
    """UI component definition."""
    id: str = Field(..., description="Component ID (kebab-case)")
    type: str = Field(..., description="Component type (input, button, table, etc.)")
    label: str = Field(default="", description="Display label")
    props: dict[str, Any] = Field(default_factory=dict, description="Component props")
    bindings: dict[str, str] = Field(default_factory=dict, description="Field bindings")


class UIPage(BaseModel):
    """UI page definition."""
    name: str = Field(..., description="Page name (snake_case)")
    route: str = Field(..., description="Route path")
    title: str = Field(..., description="Page title")
    description: str = Field(default="", description="Page purpose")
    components: list[UIComponent] = Field(default_factory=list, description="Page components")
    auth_required: bool = Field(default=False, description="Requires authentication?")
    allowed_roles: list[AuthRole] = Field(default_factory=list, description="Which roles can access")


class UISchema(BaseModel):
    """User interface schema."""
    pages: dict[str, UIPage] = Field(..., description="Map of page_name -> UIPage")
    
    def get_page(self, name: str) -> Optional[UIPage]:
        return self.pages.get(name)


class APIEndpoint(BaseModel):
    """API endpoint definition."""
    path: str = Field(..., description="API path (e.g., /api/users)")
    method: HTTPMethod = Field(..., description="HTTP method")
    name: str = Field(..., description="Endpoint identifier")
    description: str = Field(default="", description="Endpoint purpose")
    auth_required: bool = Field(default=False, description="Requires authentication?")
    allowed_roles: list[AuthRole] = Field(default_factory=list, description="Which roles can call")
    request_body: Optional[dict[str, Any]] = Field(default=None, description="Request schema")
    response_body: Optional[dict[str, Any]] = Field(default=None, description="Response schema")
    entity: Optional[str] = Field(default=None, description="Related entity (if any)")


class APISchema(BaseModel):
    """API schema definition."""
    endpoints: list[APIEndpoint] = Field(..., description="All API endpoints")
    base_path: str = Field(default="/api/v1", description="API base path")
    
    def get_endpoint(self, path: str, method: HTTPMethod) -> Optional[APIEndpoint]:
        for ep in self.endpoints:
            if ep.path == path and ep.method == method:
                return ep
        return None


class AuthConfig(BaseModel):
    """Authentication & authorization config."""
    auth_type: str = Field(..., description="auth_type (jwt, session, oauth)")
    roles: dict[AuthRole, list[str]] = Field(..., description="Role -> permissions mapping")
    premium_features: list[str] = Field(default_factory=list, description="Features gated by premium")


class GeneratedConfig(BaseModel):
    """Complete application configuration.
    
    This is the output of the entire pipeline.
    Must be valid before execution.
    """
    app_name: str = Field(..., description="Application name")
    app_description: str = Field(..., description="What the app does")
    entities: dict[str, Entity] = Field(..., description="Domain entities")
    db_schema: DBSchema = Field(..., description="Database schema")
    ui_schema: UISchema = Field(..., description="UI schema")
    api_schema: APISchema = Field(..., description="API schema")
    auth_config: AuthConfig = Field(..., description="Auth config")
    assumptions: list[str] = Field(default_factory=list, description="Assumptions made")
    notes: str = Field(default="", description="Implementation notes")


Entity.model_rebuild()
DBSchema.model_rebuild()