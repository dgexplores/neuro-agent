#!/usr/bin/env python3
"""Minimal CDK app for bootstrapping only"""
import aws_cdk as cdk

app = cdk.App()
# Empty app - just for bootstrap
app.synth()
