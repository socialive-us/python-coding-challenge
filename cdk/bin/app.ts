#!/usr/bin/env node
/**
 * Title: app.ts
 *
 * Copyright (c) 2024 Socialive. All rights reserved.
 * See all trademarks at https://www.socialive.us/terms-of-service
 */
import * as synthConfig from '../cdkSynthConfig.json';
import * as config from '../cdk.json';
import { App } from 'aws-cdk-lib';
import { PythonCodeChallengeStack } from '../lib/python-code-challenge-stack';
import { StackInputs } from '../lib/stack-inputs';
import { kebabToPascal } from '../utils/utilities';

const app = new App();

synthConfig.deployments.forEach(({ awsAccount, awsRegion, stageName }) => {
  const configKey = `${stageName}-${awsRegion}`;
  const namespace = `PythonCodeChallenge${kebabToPascal(configKey)}`;

  // Create the stack
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const context: { [key: string]: any } = config.context;
  const stackConfig = context[configKey];
  if (!stackConfig) {
    throw new SyntaxError('Failed to find configuration for ' + configKey);
  }
  const stack = new PythonCodeChallengeStack(
    app,
    `${namespace}Stack`,
    { account: awsAccount, region: awsRegion },
    stageName,
  );

  // Get the stack inputs, passed in by the pipeline factory
  const stackInputs = new StackInputs(stack);

  // Given the stack and stack inputs, create the CDK resources
  stack.setProviders(namespace, stackInputs, stackConfig);
  stack.createResources();

  // Tag the resources
  stack.tagResources(namespace);
});

app.synth();
