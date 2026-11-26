import { z } from "zod";

export const ANO_MIN = 2003;
export const ANO_MAX = 2023;
export const ANO_PADRAO = 2021;

const anoSchema = z.coerce.number().int().min(ANO_MIN).max(ANO_MAX).catch(ANO_PADRAO);

export const buscaUfSchema = z.object({ ano: z.preprocess((v) => v ?? ANO_PADRAO, anoSchema) });
export type BuscaUf = z.infer<typeof buscaUfSchema>;
