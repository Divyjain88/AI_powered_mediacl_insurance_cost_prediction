from pydantic import BaseModel, Field, computed_field,field_validator
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import Literal,Annotated

# pydantic model to validate incoming data

class UserInput(BaseModel):

    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of the user')]
    smoker: Annotated[str, Field(...,description='Is user a smoker')]
    region:Annotated[str, Field(...,description='Region of a user belongs to')]
    children:Annotated[int,Field(...,description='No. of children')]
    sex : Annotated[str,Field(...,description='Gender of the User')]
    bmi: Annotated[float,Field(...,gt=0)]



  
    @field_validator("sex")
    @classmethod
    def validate_sex(cls, value: str) -> str:
     value = value.lower()

     allowed_values = ["male", "female"]

     if value not in allowed_values:
        raise ValueError("Sex must be either 'male' or 'female'")

     return value
    
    @field_validator("region")
    @classmethod
    def validate_region(cls, value: str) -> str:
        value = value.strip().lower()

        allowed_regions = [
            "southwest",
            "southeast",
            "northwest",
            "northeast"
        ]

        if value not in allowed_regions:
            raise ValueError(
                "Region must be southwest, southeast, northwest, or northeast"
            )

        return value
   
    @computed_field
    @property
    def age_group(self) -> str:
     if self.age < 25:
        return "young"
     elif self.age < 45:
         return "adult"
     elif self.age < 60:
        return "middle_aged"
     return "senior"


    @computed_field
    @property
    def lifestyle_risk(self) -> str:
     if self.smoker and self.bmi >= 30:
        return "high"
     elif self.smoker or self.bmi >= 27:
        return "medium"
     return "low"
    
    @computed_field
    @property
    def user_region(self) -> str:
      return self.region.title() 

    @computed_field
    @property
    def family_size(self) -> int:
        return self.children + 1
