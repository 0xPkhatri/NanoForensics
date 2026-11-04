'use client';
import {useCallback, useEffect, useLayoutEffect, useRef} from 'react';
import {followDecision} from '@/lib/log-follow';

export function useLogFollow(follow: boolean, onFollow: (value:boolean)=>void, revision: string, enabled=true) {
  const viewport=useRef<HTMLDivElement>(null),content=useRef<HTMLOListElement>(null);
  const following=useRef(follow),lastTop=useRef(0),programmatic=useRef(false),intent=useRef(-Infinity),touchY=useRef(0);
  const frame=useRef(0),release=useRef(0);
  following.current=follow;
  const setFollow=useCallback((value:boolean)=>{
    following.current=value;
    if (!value) cancelAnimationFrame(frame.current);
    onFollow(value);
  },[onFollow]);
  const schedule=useCallback(()=>{
    cancelAnimationFrame(frame.current);
    frame.current=requestAnimationFrame(()=>{
      const node=viewport.current;if(!node || !following.current)return;
      programmatic.current=true;
      node.scrollTop=node.scrollHeight;lastTop.current=node.scrollTop;
      cancelAnimationFrame(release.current);
      release.current=requestAnimationFrame(()=>{programmatic.current=false});
    });
  },[]);
  useLayoutEffect(()=>{if(enabled && follow)schedule()},[enabled,follow,revision,schedule]);
  useEffect(()=>{
    if(!enabled || !content.current)return;
    const observer=new ResizeObserver(()=>{if(following.current)schedule()});
    observer.observe(content.current);
    if(viewport.current)observer.observe(viewport.current);
    return()=>{observer.disconnect();cancelAnimationFrame(frame.current);cancelAnimationFrame(release.current);programmatic.current=false};
  },[schedule,enabled]);
  const userIntent=()=>{intent.current=performance.now()};
  return {viewport,content,setFollow,pause:()=>setFollow(false),jump:()=>{setFollow(true);schedule()},
    handlers:{
      onScroll:()=>{
        const node=viewport.current;if(!node)return;
        const action=followDecision({top:node.scrollTop,previousTop:lastTop.current,height:node.scrollHeight,viewport:node.clientHeight,following:following.current,programmatic:programmatic.current,userIntent:performance.now()-intent.current<1500});
        lastTop.current=node.scrollTop;
        if(action==='pause')setFollow(false);else if(action==='resume')setFollow(true);
      },
      onWheel:(event:React.WheelEvent)=>{
        userIntent();const node=viewport.current;if(!node || node.scrollHeight<=node.clientHeight+2)return;
        if(event.deltaY<0)setFollow(false);
        else if(node.scrollHeight-node.clientHeight-node.scrollTop<=18)setFollow(true);
      },
      onPointerDown:userIntent,
      onTouchStart:(event:React.TouchEvent)=>{userIntent();touchY.current=event.touches[0]?.clientY||0},
      onTouchMove:(event:React.TouchEvent)=>{
        userIntent();const y=event.touches[0]?.clientY||0;
        if(y>touchY.current+2)setFollow(false);touchY.current=y;
      },
      onKeyDown:(event:React.KeyboardEvent)=>{
        if(event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement)return;
        userIntent();if(['ArrowUp','PageUp','Home'].includes(event.key))setFollow(false);
      },
    }};
}
