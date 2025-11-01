#!/bin/bash
# LoopLabs quick job launcher

curl -X POST http://127.0.0.1:3000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt":"Product promo video",
    "media":["assets/logo.png"],
    "keywords":["modern","clean"],
    "hashtags":["#promo","#looplabs"],
    "audio":"energetic",
    "brand":"LoopLabs",
    "theme":"blue"
  }'
