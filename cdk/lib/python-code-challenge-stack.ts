/**
 * Title: python-code-challenge-stack.ts
 *
 * Copyright (c) 2024 Socialive. All rights reserved.
 * See all trademarks at https://www.socialive.us/terms-of-service
 */
import { App, Environment, Stack, Tags } from 'aws-cdk-lib';
import { PythonCodeChallengeConfig } from './python-code-challenge-config';
import { StackInputs } from './stack-inputs';


export class PythonCodeChallengeStack extends Stack {

  public constructor(
    app: App,
    id: string,
    private env: Environment,
    private readonly deploymentStage: string,
  ) {
    super(app, id, { env });
  }

  public setProviders(namespace: string, stackInputs: StackInputs, config: PythonCodeChallengeConfig): void {
    const fullConfig = this.getDefaults(namespace, config);
  }

  public createResources(): void {
  }

  public tagResources(namespace: string): void {
    Tags.of(this).add('Product', 'Socialive');
    Tags.of(this).add('ProductDetail', 'python-code-challenge');
    Tags.of(this).add('Namespace', namespace);
  }

  private getDefaults(namespace: string, config: PythonCodeChallengeConfig): PythonCodeChallengeConfig {
    return {
    }
  }
}
