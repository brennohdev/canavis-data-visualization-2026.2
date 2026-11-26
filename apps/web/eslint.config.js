import js from "@eslint/js";
import jsxA11y from "eslint-plugin-jsx-a11y";
import reactHooks from "eslint-plugin-react-hooks";
import globals from "globals";
import tseslint from "typescript-eslint";

const catalogo = "Veja docs/entrega-etapa3/catalogo-componentes.md.";

const paletaPadrao =
  "(bg|text|border|ring|fill|stroke|from|to|via|outline|divide|decoration|shadow|accent|caret)";
const familiasPadrao =
  "(slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)";
const tokensSoDeForma = "(abaixo|serie-2|acucar|etanol|neutro-dado|ausente|grade|eixo)";

function proibirString(regex, message) {
  return [
    { selector: `Literal[value=/${regex}/]`, message },
    { selector: `TemplateElement[value.raw=/${regex}/]`, message },
  ];
}

const regrasDeString = [
  ...proibirString(
    `(^|[^\\w-])${paletaPadrao}-(white|black|${familiasPadrao}-\\d{2,3})($|[^\\w-])`,
    `Cor da paleta padrão do Tailwind não é permitida. Use um token de cor. ${catalogo}`,
  ),
  ...proibirString(
    "(^|[^\\w&])#[0-9a-fA-F]{3,8}($|[^\\w])",
    `Cor hexadecimal literal não é permitida. Use um token de cor. ${catalogo}`,
  ),
  ...proibirString(
    `(^|[\\s:!])text-${tokensSoDeForma}($|[\\s/])`,
    `Este token é só de forma e não serve para texto. Use a variante -texto. ${catalogo}`,
  ),
];

const regrasDeClasse = [
  {
    selector: "JSXAttribute[name.name='className']",
    message: `Rotas não recebem className. Componha componentes de src/components. ${catalogo}`,
  },
  {
    selector: "JSXAttribute[name.name='style']",
    message: `Rotas não recebem style. Componha componentes de src/components. ${catalogo}`,
  },
];

const importsDeClasse = {
  paths: ["clsx", "class-variance-authority", "tailwind-merge", "@/lib/utils"].map((name) => ({
    name,
    message: `Montar classes só é permitido em src/components. ${catalogo}`,
  })),
};

export default tseslint.config(
  { ignores: ["dist", "node_modules"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: { globals: globals.browser },
    plugins: { "react-hooks": reactHooks },
    rules: reactHooks.configs.recommended.rules,
  },
  { ...jsxA11y.flatConfigs.recommended, files: ["src/**/*.tsx"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    rules: { "no-restricted-syntax": ["error", ...regrasDeString] },
  },
  {
    files: ["src/**/*.{ts,tsx}"],
    ignores: ["src/components/**", "src/lib/utils.ts"],
    rules: {
      "no-restricted-syntax": ["error", ...regrasDeString, ...regrasDeClasse],
      "no-restricted-imports": ["error", importsDeClasse],
    },
  },
  {
    files: ["**/conformidade.test.ts"],
    rules: { "no-restricted-syntax": "off" },
  },
  {
    files: ["*.config.{js,ts}"],
    languageOptions: { globals: globals.node },
  },
);
