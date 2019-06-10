#!/usr/bin/env python3
"""
pip3 install imgkit requests printable
"""
import os, sys
import json

import imgkit
import requests
from printable import readable

version = "0.4"


def http_post_json(url, data=None, is_json=True, encoding="utf8"):
    res = requests.post(url, data=data)
    if encoding:
        res.encoding = encoding

    err = False if res.status_code == 200 else res.status_code
    data = res.json() if is_json else res.text
    return err, data


def post_github(text, mode, context):
    """Send a POST request to GitHub via API """
    payload = {"text": text, "mode": mode}

    if context != None:
        payload["context"] = context

    err, r = http_post_json(
        "https://api.github.com/markdown",
        data=json.dumps(payload),
        is_json=False
    )
    if err:
        print(err)
        raise Exception(f"github api error code {err}: {r}")
    return r


def csv2png(data, outfile, prefix=None, suffix=None, title=""):
    if isinstance(data, str):
        with open(data) as f:
            data = json.load(f)

    md = readable(data, grid='markdown')
    md = '\n'.join(['|' + l + '|' for l in md.split('\n')])

    if title:
        md = f"{title}\n\n{md}"

    html = post_github(md, 'markdown', None)
    html = render_page(html, prefix=prefix, suffix=suffix)
    if os.getenv("DEBUG"):
        print(html, file=sys.stderr)
    imgkit.from_string(
        html,
        outfile,
        options={
            'encoding': 'UTF-8',
            'quiet': None,
            'format': 'png',
            'enable-smart-width': None,
        }
    )


def render_page(body, prefix=None, suffix=None):
    prefix = prefix or """
    <html>
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {
      max-width: 1366px;
      border: 1px solid #ddd;
      margin: 6px;
      zoom: 0.9;
    }

    body .markdown-body
    {
      padding: 15px;
    }

    @font-face {
      font-family: fontawesome-mini;
      src: url(data:font/woff;charset=utf-8;base64,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) format('woff');
    }

    .markdown-body {
      -ms-text-size-adjust: 100%;
      -webkit-text-size-adjust: 100%;
      color: #333333;
      overflow: hidden;
      font-family: "Helvetica Neue", Helvetica, "Segoe UI", Arial, freesans,
        "Inconsolata", Coda, "Microsoft Yahei", "Helvetica Neue",
        Helvetica, "Nimbus Sans L", Arial, "Liberation Sans", "PingFang SC",
        "Hiragino Sans GB", "Source Han Sans CN", "Source Han Sans SC",
        "Wenquanyi Micro Hei", "WenQuanYi Zen Hei", "ST Heiti", SimHei,
        "WenQuanYi Zen Hei Sharp", noto, sans-serif, fontawesome-mini;
      font-size: 16px;
      line-height: 1.6;
      word-wrap: break-word;
    }

    .markdown-body a {
      background: transparent;
    }

    .markdown-body a:active,
    .markdown-body a:hover {
      outline: 0;
    }

    .markdown-body b,
    .markdown-body strong {
      font-weight: bold;
    }

    .markdown-body mark {
      background: #ff0;
      color: #000;
      font-style: italic;
      font-weight: bold;
    }

    .markdown-body sub,
    .markdown-body sup {
      font-size: 75%;
      line-height: 0;
      position: relative;
      vertical-align: baseline;
    }
    .markdown-body sup {
      top: -0.5em;
    }
    .markdown-body sub {
      bottom: -0.25em;
    }

    .markdown-body h1 {
      font-size: 2em;
      margin: 0.67em 0;
    }

    .markdown-body img {
      border: 0;
    }

    .markdown-body hr {
      -moz-box-sizing: content-box;
      box-sizing: content-box;
      height: 0;
    }

    .markdown-body pre {
      overflow: auto;
    }

    .markdown-body code,
    .markdown-body kbd,
    .markdown-body pre,
    .markdown-body samp {
      font-family: "Source Code Pro", monospace;
      font-size: 1em;
    }

    .markdown-body input {
      color: inherit;
      font: inherit;
      margin: 0;
    }

    .markdown-body html input[disabled] {
      cursor: default;
    }

    .markdown-body input {
      line-height: normal;
    }

    .markdown-body input[type="checkbox"] {
      box-sizing: border-box;
      padding: 0;
    }

    .markdown-body table {
      border-collapse: collapse;
      border-spacing: 0;
    }

    .markdown-body td,
    .markdown-body th {
      padding: 0;
    }

    .markdown-body .codehilitetable {
      border: 0;
      border-spacing: 0;
    }

    .markdown-body .codehilitetable tr {
      border: 0;
    }

    .markdown-body .codehilitetable pre,
    .markdown-body .codehilitetable div.codehilite {
      margin: 0;
    }

    .markdown-body .linenos,
    .markdown-body .code,
    .markdown-body .codehilitetable td {
      border: 0;
      padding: 0;
    }

    .markdown-body td:not(.linenos) .linenodiv {
      padding: 0 !important;
    }

    .markdown-body .code {
      width: 100%;
    }

    .markdown-body .linenos div pre,
    .markdown-body .linenodiv pre,
    .markdown-body .linenodiv {
      border: 0;
      -webkit-border-radius: 0;
      -moz-border-radius: 0;
      border-radius: 0;
      -webkit-border-top-left-radius: 3px;
      -webkit-border-bottom-left-radius: 3px;
      -moz-border-radius-topleft: 3px;
      -moz-border-radius-bottomleft: 3px;
      border-top-left-radius: 3px;
      border-bottom-left-radius: 3px;
    }

    .markdown-body .code div pre,
    .markdown-body .code div {
      border: 0;
      -webkit-border-radius: 0;
      -moz-border-radius: 0;
      border-radius: 0;
      -webkit-border-top-right-radius: 3px;
      -webkit-border-bottom-right-radius: 3px;
      -moz-border-radius-topright: 3px;
      -moz-border-radius-bottomright: 3px;
      border-top-right-radius: 3px;
      border-bottom-right-radius: 3px;
    }

    .markdown-body * {
      -moz-box-sizing: border-box;
      box-sizing: border-box;
    }

    .markdown-body input {
      font: 13px Helvetica, arial, freesans, clean, sans-serif, "Segoe UI Emoji", "Segoe UI Symbol";
      line-height: 1.4;
    }

    .markdown-body a {
      color: #4183c4;
      text-decoration: none;
    }

    .markdown-body a:hover,
    .markdown-body a:focus,
    .markdown-body a:active {
      text-decoration: underline;
    }

    .markdown-body hr {
      height: 0;
      margin: 15px 0;
      overflow: hidden;
      background: transparent;
      border: 0;
      border-bottom: 1px solid #ddd;
    }

    .markdown-body hr:before,
    .markdown-body hr:after {
      display: table;
      content: " ";
    }

    .markdown-body hr:after {
      clear: both;
    }

    .markdown-body h1,
    .markdown-body h2,
    .markdown-body h3,
    .markdown-body h4,
    .markdown-body h5,
    .markdown-body h6 {
      margin-top: 15px;
      margin-bottom: 15px;
      line-height: 1.1;
    }

    .markdown-body h1 {
      font-size: 30px;
    }

    .markdown-body h2 {
      font-size: 21px;
    }

    .markdown-body h3 {
      font-size: 16px;
    }

    .markdown-body h4 {
      font-size: 14px;
    }

    .markdown-body h5 {
      font-size: 12px;
    }

    .markdown-body h6 {
      font-size: 11px;
    }

    .markdown-body blockquote {
      margin: 0;
    }

    .markdown-body ul,
    .markdown-body ol {
      padding: 0;
      margin-top: 0;
      margin-bottom: 0;
    }

    .markdown-body ol ol,
    .markdown-body ul ol {
      list-style-type: lower-roman;
    }

    .markdown-body ul ul ol,
    .markdown-body ul ol ol,
    .markdown-body ol ul ol,
    .markdown-body ol ol ol {
      list-style-type: lower-alpha;
    }

    .markdown-body dd {
      margin-left: 0;
    }

    .markdown-body code,
    .markdown-body pre,
    .markdown-body samp {
      font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
      font-size: 12px;
    }

    .markdown-body pre {
      margin-top: 0;
      margin-bottom: 0;
    }

    .markdown-body kbd {
      background-color: #e7e7e7;
      background-image: -moz-linear-gradient(#fefefe, #e7e7e7);
      background-image: -webkit-linear-gradient(#fefefe, #e7e7e7);
      background-image: linear-gradient(#fefefe, #e7e7e7);
      background-repeat: repeat-x;
      border-radius: 2px;
      border: 1px solid #cfcfcf;
      color: #000;
      padding: 3px 5px;
      line-height: 10px;
      font: 11px Consolas, "Liberation Mono", Menlo, Courier, monospace;
      display: inline-block;
    }

    .markdown-body>*:first-child {
      margin-top: 0 !important;
    }

    .markdown-body>*:last-child {
      margin-bottom: 0 !important;
    }

    .markdown-body .headerlink {
      font: normal 400 16px fontawesome-mini;
      vertical-align: middle;
      margin-left: -16px;
      float: left;
      display: inline-block;
      text-decoration: none;
      opacity: 0;
      color: #333;
    }

    .markdown-body .headerlink:focus {
      outline: none;
    }

    .markdown-body h1 .headerlink {
      margin-top: 0.8rem;
    }

    .markdown-body h2 .headerlink,
    .markdown-body h3 .headerlink {
      margin-top: 0.6rem;
    }

    .markdown-body h4 .headerlink {
      margin-top: 0.2rem;
    }

    .markdown-body h5 .headerlink,
    .markdown-body h6 .headerlink {
      margin-top: 0;
    }

    .markdown-body .headerlink:hover,
    .markdown-body h1:hover .headerlink,
    .markdown-body h2:hover .headerlink,
    .markdown-body h3:hover .headerlink,
    .markdown-body h4:hover .headerlink,
    .markdown-body h5:hover .headerlink,
    .markdown-body h6:hover .headerlink {
      opacity: 1;
      text-decoration: none;
    }

    .markdown-body h1 {
      padding-bottom: 0.3em;
      font-size: 2.25em;
      line-height: 1.2;
      border-bottom: 1px solid #eee;
    }

    .markdown-body h2 {
      padding-bottom: 0.3em;
      font-size: 1.75em;
      line-height: 1.225;
      border-bottom: 1px solid #eee;
    }

    .markdown-body h3 {
      font-size: 1.5em;
      line-height: 1.43;
    }

    .markdown-body h4 {
      font-size: 1.25em;
    }

    .markdown-body h5 {
      font-size: 1em;
    }

    .markdown-body h6 {
      font-size: 1em;
      color: #777;
    }

    .markdown-body p,
    .markdown-body blockquote,
    .markdown-body ul,
    .markdown-body ol,
    .markdown-body dl,
    .markdown-body table,
    .markdown-body pre,
    .markdown-body .admonition {
      margin-top: 0;
      margin-bottom: 16px;
    }

    .markdown-body hr {
      height: 4px;
      padding: 0;
      margin: 16px 0;
      background-color: #e7e7e7;
      border: 0 none;
    }

    .markdown-body ul,
    .markdown-body ol {
      padding-left: 2em;
    }

    .markdown-body ul ul,
    .markdown-body ul ol,
    .markdown-body ol ol,
    .markdown-body ol ul {
      margin-top: 0;
      margin-bottom: 0;
    }

    .markdown-body li>p {
      margin-top: 16px;
    }

    .markdown-body dl {
      padding: 0;
    }

    .markdown-body dl dt {
      padding: 0;
      margin-top: 16px;
      font-size: 1em;
      font-style: italic;
      font-weight: bold;
    }

    .markdown-body dl dd {
      padding: 0 16px;
      margin-bottom: 16px;
    }

    .markdown-body blockquote {
      padding: 0 15px;
      color: #777;
      border-left: 4px solid #ddd;
    }

    .markdown-body blockquote>:first-child {
      margin-top: 0;
    }

    .markdown-body blockquote>:last-child {
      margin-bottom: 0;
    }

    .markdown-body table {
      display: block;
      width: 100%;
      overflow: auto;
      word-break: normal;
      word-break: keep-all;
    }

    .markdown-body table th {
      font-weight: bold;
    }

    .markdown-body table th,
    .markdown-body table td {
      padding: 6px 13px;
      border: 1px solid #ddd;
    }

    .markdown-body table tr {
      background-color: #fff;
      border-top: 1px solid #ccc;
    }

    .markdown-body table tr:nth-child(2n) {
      background-color: #f8f8f8;
    }

    .markdown-body img {
      max-width: 100%;
      -moz-box-sizing: border-box;
      box-sizing: border-box;
    }

    .markdown-body code,
    .markdown-body samp {
      padding: 0;
      padding-top: 0.2em;
      padding-bottom: 0.2em;
      margin: 0;
      font-size: 85%;
      background-color: rgba(0,0,0,0.04);
      border-radius: 3px;
    }

    .markdown-body code:before,
    .markdown-body code:after {
      letter-spacing: -0.2em;
      content: " ";
    }

    .markdown-body pre>code {
      padding: 0;
      margin: 0;
      font-size: 100%;
      word-break: normal;
      white-space: pre;
      background: transparent;
      border: 0;
    }

    .markdown-body .codehilite {
      margin-bottom: 16px;
    }

    .markdown-body .codehilite pre,
    .markdown-body pre {
      padding: 16px;
      overflow: auto;
      font-size: 85%;
      line-height: 1.45;
      background-color: #f7f7f7;
      border-radius: 3px;
    }

    .markdown-body .codehilite pre {
      margin-bottom: 0;
      word-break: normal;
    }

    .markdown-body pre {
      word-wrap: normal;
    }

    .markdown-body pre code {
      display: inline;
      max-width: initial;
      padding: 0;
      margin: 0;
      overflow: initial;
      line-height: inherit;
      word-wrap: normal;
      background-color: transparent;
      border: 0;
    }

    .markdown-body pre code:before,
    .markdown-body pre code:after {
      content: normal;
    }

    /* Admonition */
    .markdown-body .admonition {
      -webkit-border-radius: 3px;
      -moz-border-radius: 3px;
      position: relative;
      border-radius: 3px;
      border: 1px solid #e0e0e0;
      border-left: 6px solid #333;
      padding: 10px 10px 10px 30px;
    }

    .markdown-body .admonition table {
      color: #333;
    }

    .markdown-body .admonition p {
      padding: 0;
    }

    .markdown-body .admonition-title {
      font-weight: bold;
      margin: 0;
    }

    .markdown-body .admonition>.admonition-title {
      color: #333;
    }

    .markdown-body .attention>.admonition-title {
      color: #a6d796;
    }

    .markdown-body .caution>.admonition-title {
      color: #d7a796;
    }

    .markdown-body .hint>.admonition-title {
      color: #96c6d7;
    }

    .markdown-body .danger>.admonition-title {
      color: #c25f77;
    }

    .markdown-body .question>.admonition-title {
      color: #96a6d7;
    }

    .markdown-body .note>.admonition-title {
      color: #d7c896;
    }

    .markdown-body .admonition:before,
    .markdown-body .attention:before,
    .markdown-body .caution:before,
    .markdown-body .hint:before,
    .markdown-body .danger:before,
    .markdown-body .question:before,
    .markdown-body .note:before {
      font: normal normal 16px fontawesome-mini;
      -moz-osx-font-smoothing: grayscale;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
      line-height: 1.5;
      color: #333;
      position: absolute;
      left: 0;
      top: 0;
      padding-top: 10px;
      padding-left: 10px;
    }

    .markdown-body .admonition:before {
      content: "\f056\00a0";
      color: 333;
    }

    .markdown-body .attention:before {
      content: "\f058\00a0";
      color: #a6d796;
    }

    .markdown-body .caution:before {
      content: "\f06a\00a0";
      color: #d7a796;
    }

    .markdown-body .hint:before {
      content: "\f05a\00a0";
      color: #96c6d7;
    }

    .markdown-body .danger:before {
      content: "\f057\00a0";
      color: #c25f77;
    }

    .markdown-body .question:before {
      content: "\f059\00a0";
      color: #96a6d7;
    }

    .markdown-body .note:before {
      content: "\f040\00a0";
      color: #d7c896;
    }

    .markdown-body .admonition::after {
      content: normal;
    }

    .markdown-body .attention {
      border-left: 6px solid #a6d796;
    }

    .markdown-body .caution {
      border-left: 6px solid #d7a796;
    }

    .markdown-body .hint {
      border-left: 6px solid #96c6d7;
    }

    .markdown-body .danger {
      border-left: 6px solid #c25f77;
    }

    .markdown-body .question {
      border-left: 6px solid #96a6d7;
    }

    .markdown-body .note {
      border-left: 6px solid #d7c896;
    }

    .markdown-body .admonition>*:first-child {
      margin-top: 0 !important;
    }

    .markdown-body .admonition>*:last-child {
      margin-bottom: 0 !important;
    }

    /* progress bar*/
    .markdown-body .progress {
      display: block;
      width: 300px;
      margin: 10px 0;
      height: 24px;
      -webkit-border-radius: 3px;
      -moz-border-radius: 3px;
      border-radius: 3px;
      background-color: #ededed;
      position: relative;
      box-shadow: inset -1px 1px 3px rgba(0, 0, 0, .1);
    }

    .markdown-body .progress-label {
      position: absolute;
      text-align: center;
      font-weight: bold;
      width: 100%; margin: 0;
      line-height: 24px;
      color: #333;
      text-shadow: 1px 1px 0 #fefefe, -1px -1px 0 #fefefe, -1px 1px 0 #fefefe, 1px -1px 0 #fefefe, 0 1px 0 #fefefe, 0 -1px 0 #fefefe, 1px 0 0 #fefefe, -1px 0 0 #fefefe, 1px 1px 2px #000;
      -webkit-font-smoothing: antialiased !important;
      white-space: nowrap;
      overflow: hidden;
    }

    .markdown-body .progress-bar {
      height: 24px;
      float: left;
      -webkit-border-radius: 3px;
      -moz-border-radius: 3px;
      border-radius: 3px;
      background-color: #96c6d7;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, .5), inset 0 -1px 0 rgba(0, 0, 0, .1);
      background-size: 30px 30px;
      background-image: -webkit-linear-gradient(
        135deg, rgba(255, 255, 255, .4) 27%,
        transparent 27%,
        transparent 52%, rgba(255, 255, 255, .4) 52%,
        rgba(255, 255, 255, .4) 77%,
        transparent 77%, transparent
      );
      background-image: -moz-linear-gradient(
        135deg,
        rgba(255, 255, 255, .4) 27%, transparent 27%,
        transparent 52%, rgba(255, 255, 255, .4) 52%,
        rgba(255, 255, 255, .4) 77%, transparent 77%,
        transparent
      );
      background-image: -ms-linear-gradient(
        135deg,
        rgba(255, 255, 255, .4) 27%, transparent 27%,
        transparent 52%, rgba(255, 255, 255, .4) 52%,
        rgba(255, 255, 255, .4) 77%, transparent 77%,
        transparent
      );
      background-image: -o-linear-gradient(
        135deg,
        rgba(255, 255, 255, .4) 27%, transparent 27%,
        transparent 52%, rgba(255, 255, 255, .4) 52%,
        rgba(255, 255, 255, .4) 77%, transparent 77%,
        transparent
      );
      background-image: linear-gradient(
        135deg,
        rgba(255, 255, 255, .4) 27%, transparent 27%,
        transparent 52%, rgba(255, 255, 255, .4) 52%,
        rgba(255, 255, 255, .4) 77%, transparent 77%,
        transparent
      );
    }

    .markdown-body .progress-100plus .progress-bar {
      background-color: #a6d796;
    }

    .markdown-body .progress-80plus .progress-bar {
      background-color: #c6d796;
    }

    .markdown-body .progress-60plus .progress-bar {
      background-color: #d7c896;
    }

    .markdown-body .progress-40plus .progress-bar {
      background-color: #d7a796;
    }

    .markdown-body .progress-20plus .progress-bar {
      background-color: #d796a6;
    }

    .markdown-body .progress-0plus .progress-bar {
      background-color: #c25f77;
    }

    .markdown-body .candystripe-animate .progress-bar{
      -webkit-animation: animate-stripes 3s linear infinite;
      -moz-animation: animate-stripes 3s linear infinite;
      animation: animate-stripes 3s linear infinite;
    }

    @-webkit-keyframes animate-stripes {
      0% {
        background-position: 0 0;
      }

      100% {
        background-position: 60px 0;
      }
    }

    @-moz-keyframes animate-stripes {
      0% {
        background-position: 0 0;
      }

      100% {
        background-position: 60px 0;
      }
    }

    @keyframes animate-stripes {
      0% {
        background-position: 0 0;
      }

      100% {
        background-position: 60px 0;
      }
    }

    .markdown-body .gloss .progress-bar {
      box-shadow:
        inset 0 4px 12px rgba(255, 255, 255, .7),
        inset 0 -12px 0 rgba(0, 0, 0, .05);
    }

    /* MultiMarkdown Critic Blocks */
    .markdown-body .critic_mark {
      background: #ff0;
    }

    .markdown-body .critic_delete {
      color: #c82829;
      text-decoration: line-through;
    }

    .markdown-body .critic_insert {
      color: #718c00 ;
      text-decoration: underline;
    }

    .markdown-body .critic_comment {
      color: #8e908c;
      font-style: italic;
    }

    .markdown-body .headeranchor {
      font: normal normal 16px fontawesome-mini;
      line-height: 1;
      display: inline-block;
      text-decoration: none;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      -webkit-user-select: none;
      -moz-user-select: none;
      -ms-user-select: none;
      user-select: none;
    }

    .headeranchor:before {
      content: '\e157';
    }

    .markdown-body .task-list-item {
      list-style-type: none;
    }

    .markdown-body .task-list-item+.task-list-item {
      margin-top: 3px;
    }

    .markdown-body .task-list-item input {
      margin: 0 4px 0.25em -20px;
      vertical-align: middle;
    }

    /* Media */
    @media only screen and (min-width: 480px) {
      .markdown-body {
        font-size:14px;
      }
    }

    @media only screen and (min-width: 768px) {
      .markdown-body {
        font-size:16px;
      }
    }

    @media print {
      .markdown-body * {
        background: transparent !important;
        color: black !important;
        filter:none !important;
        -ms-filter: none !important;
      }

      .markdown-body {
        font-size:12pt;
        max-width:100%;
        outline:none;
        border: 0;
      }

      .markdown-body a,
      .markdown-body a:visited {
        text-decoration: underline;
      }

      .markdown-body .headeranchor-link {
        display: none;
      }

      .markdown-body a[href]:after {
        content: " (" attr(href) ")";
      }

      .markdown-body abbr[title]:after {
        content: " (" attr(title) ")";
      }

      .markdown-body .ir a:after,
      .markdown-body a[href^="javascript:"]:after,
      .markdown-body a[href^="#"]:after {
        content: "";
      }

      .markdown-body pre {
        white-space: pre;
        white-space: pre-wrap;
        word-wrap: break-word;
      }

      .markdown-body pre,
      .markdown-body blockquote {
        border: 1px solid #999;
        padding-right: 1em;
        page-break-inside: avoid;
      }

      .markdown-body .progress,
      .markdown-body .progress-bar {
        -moz-box-shadow: none;
        -webkit-box-shadow: none;
        box-shadow: none;
      }

      .markdown-body .progress {
        border: 1px solid #ddd;
      }

      .markdown-body .progress-bar {
        height: 22px;
        border-right: 1px solid #ddd;
      }

      .markdown-body tr,
      .markdown-body img {
        page-break-inside: avoid;
      }

      .markdown-body img {
        max-width: 100% !important;
      }

      .markdown-body p,
      .markdown-body h2,
      .markdown-body h3 {
        orphans: 3;
        widows: 3;
      }

      .markdown-body h2,
      .markdown-body h3 {
        page-break-after: avoid;
      }
    }
    </style>
    </head>
    <body>
    <div class="markdown-body">
    """
    suffix = suffix or "</div></body></html>"
    return prefix + body + suffix
