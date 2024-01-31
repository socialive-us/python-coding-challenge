/**
 * Title: stack-inputs.ts
 *
 * Copyright (c) 2024 Socialive. All rights reserved.
 * See all trademarks at https://www.socialive.us/terms-of-service
 */
import { CfnParameter } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class StackInputs {
  readonly awsRegion: string;
  readonly stageName: string;

  constructor(scope: Construct) {
    this.awsRegion = new CfnParameter(scope, 'awsRegion', {
      type: 'String',
      description: 'AWS region',
    }).valueAsString;
    this.stageName = new CfnParameter(scope, 'stageName', {
      type: 'String',
      description: 'Deployment stage name',
    }).valueAsString;
  }
}
