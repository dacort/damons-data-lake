#!/usr/bin/env python3
import os

from aws_cdk import core as cdk

from data_containers.data_containers_stack import DataContainersStack, GlueStack


app = cdk.App()
DataContainersStack(app, "DataContainersStack")
GlueStack(app, "GlueStack")

app.synth()
