from dataclasses import dataclass
from typing import List
from pprint import pprint
import re
import boto3
from botocore.model import OperationModel

# TODO: yield all the top-level output members as well because that is part of the program input
# Some of the operations can be discarded immediately because they don't have output shapes.

# TODO: pick the operation list and unpickle it for further work. it appears that instantiating the client is the slowest part of the process.

def yield_operation_models():

    session = boto3.Session(region_name="us-east-1")
    for service_name in session.get_available_services():
        service_model = session.client(service_name).meta.service_model
        for operation_name in service_model.operation_names:
            yield service_model.operation_model(operation_name)

# Include operations:
#
# * with a reading verb
# * with an output shape
# * with no required inputs
# * with an output shape type structure
# * with one required member in the structure
# * with the required member being a list
# * with each member of the list being a structure
# * with each required member of the structure being a scalar

def write_operation(operation_model):

    operation = Operation(operation_model)

    if operation.name.verb not in ["Describe", "List", "Get", "View"]:
        print(f"{operation.service_name} {operation.name} is not a reading verb")
    
    elif operation.output_shape is None:
        print(f"{operation.service_name} {operation.name} has no output shape")
    
    elif len(operation.required_inputs) > 0:
        print(f"{operation.service_name} {operation.name} has required inputs")
    
    elif operation.output_shape_type_name != "structure":
        print(f"{operation.service_name} {operation.name} does not have an output structure")

    # It's okay if there are zero; we assume the first one is the list
    elif len(operation.required_outputs) > 1:
        print(f"{operation.service_name} {operation.name} has multiple required outputs")

    elif operation.first_output_member_type != "list":
        print(f"{operation.service_name} {operation.name} has non-list first output member")

    else:
        pprint(operation)


@dataclass
class OperationName(object):

    verb: str
    noun: str


    @classmethod
    def parse_name(cls, model: OperationModel):

        parts = re.split("(?=[A-Z])", model.name, maxsplit=2)
        verb = parts[1]
        noun = parts[2] if len(parts) > 2 else None
        return OperationName(verb, noun)


    @property
    def name(self):

        return self.verb + (self.noun or "")


    def __repr__(self):

        return repr(self.name)
    

    def __str__(self):

        return self.name


@dataclass
class Operation(object):

    model: OperationModel


    @property
    def service_name(self):
        return self.model.service_model.service_name


    @property
    def name(self):
        return OperationName.parse_name(self.model)


    @property
    def input_shape(self):
        return self.model.input_shape


    @property
    def output_shape(self):
        return self.model.output_shape
    

    @property
    def required_inputs(self):
        return self.model.input_shape.required_members if self.model.input_shape else []


    @property
    def output_shape_type_name(self):
        return self.model.output_shape.type_name if self.model.output_shape else None


    @property
    def required_outputs(self):
        return self.model.output_shape.required_members if self.model.output_shape else None
    

    @property
    def first_output_member(self):

        shape = self.model.output_shape
        if shape:
            return next(iter(shape.members))

    @property
    def first_output_member_type(self):

        return self.output_shape.members[self.first_output_member].type_name


for op in yield_operation_models():
    write_operation(op)
