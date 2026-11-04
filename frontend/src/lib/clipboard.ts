export async function copyLogText(value:string):Promise<void> {
  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    try {await navigator.clipboard.writeText(value);return}catch{/* Try the local fallback. */}
  }
  if (typeof document === 'undefined' || typeof document.execCommand !== 'function') throw new Error('Clipboard is unavailable. Use the download controls instead.');
  const previous=document.activeElement as HTMLElement|null;
  const selection=document.getSelection(),ranges:Range[]=[];
  if(selection)for(let i=0;i<selection.rangeCount;i++)ranges.push(selection.getRangeAt(i));
  const field=document.createElement('textarea');field.value=value;field.readOnly=true;
  field.style.cssText='position:fixed;left:-10000px;top:0';document.body.appendChild(field);
  try {
    field.select();field.setSelectionRange(0,field.value.length);
    if(!document.execCommand('copy'))throw new Error('Copy was blocked. Use Download JSON or Download .log.');
  } finally {
    field.remove();previous?.focus({preventScroll:true});
    if(selection){selection.removeAllRanges();for(const range of ranges)selection.addRange(range)}
  }
}
