/**
 * Title: utilities.ts
 *
 * Copyright (c) 2024 Socialive. All rights reserved.
 * See all trademarks at https://www.socialive.us/terms-of-service
 */

export const kebabToPascal = (string : string): string => {
  const camel = kebabToCamel(string);
  return capitalizeFirstLetter(camel);
};

const kebabToCamel = (string: string): string =>
  string.replace(/-./g, (x: string) => x.toUpperCase()[1]);

const capitalizeFirstLetter = (string: string): string =>
  string.charAt(0).toUpperCase() + string.slice(1);
