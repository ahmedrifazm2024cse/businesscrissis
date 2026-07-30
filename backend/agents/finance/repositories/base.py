from typing import TypeVar, Generic, Type, List, Optional, Any, Dict
from beanie import Document, PydanticObjectId
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=Document)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, id: Any) -> Optional[ModelType]:
        # Depending on how IDs are defined, if using default PydanticObjectId:
        return await self.model.get(id)

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        return await self.model.find_one({field: value})

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return await self.model.find_all().skip(skip).limit(limit).to_list()

    async def get_multi_by_query(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[ModelType]:
        return await self.model.find(query).skip(skip).limit(limit).to_list()

    async def create(self, obj_in: Dict[str, Any] | BaseModel) -> ModelType:
        if isinstance(obj_in, dict):
            db_obj = self.model(**obj_in)
        else:
            db_obj = self.model(**obj_in.model_dump())
        await db_obj.insert()
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: Dict[str, Any] | BaseModel) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        await db_obj.save()
        return db_obj

    async def remove(self, id: Any) -> bool:
        obj = await self.get(id)
        if obj:
            await obj.delete()
            return True
        return False
