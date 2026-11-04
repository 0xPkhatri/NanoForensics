// Tests use the already-installed TypeScript compiler to inspect actual JSX output.
import {registerHooks} from 'node:module';
import {readFileSync,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import ts from 'typescript';
export function registerTestTSX(){return registerHooks({
  resolve(specifier,context,next){
    if(specifier.startsWith('@/')){
      for(const extension of ['.ts','.tsx']){
        const url=new URL('../src/'+specifier.slice(2)+extension,import.meta.url);
        if(existsSync(fileURLToPath(url)))return {url:url.href,shortCircuit:true};
      }
    }
    if(specifier.startsWith('.') && context.parentURL && !/\.\w+$/.test(specifier)){
      for(const extension of ['.ts','.tsx']){
        const url=new URL(specifier+extension,context.parentURL);
        if(existsSync(fileURLToPath(url)))return {url:url.href,shortCircuit:true};
      }
    }
    return next(specifier,context);
  },
  load(url,context,next){
    if(url.endsWith('.tsx'))return {format:'module',shortCircuit:true,source:ts.transpileModule(readFileSync(fileURLToPath(url),'utf8'),{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.ReactJSX}}).outputText};
    return next(url,context);
  },
})}
