export const getMongoId = (input: string): string | null => {
  const match = /[0-9a-fA-F]{24}/.exec(input);
  return match ? match[0] : null;
};
