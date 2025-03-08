// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var titles = {};

function f(tabId, changeInfo, tab) {
  if (changeInfo.title) {
    if (!titles[tabId]) {
      titles[tabId] = changeInfo.title
    } else if (titles[tabId] === changeInfo.title) {
      // do nothing
    } else {
      chrome.tabs.query({}, function(tabs) {
        tabs.forEach(t => {
          if (t.id != tabId) {
            chrome.scripting.executeScript({target: { tabId: t.id },
              // hacky way to include jQuery
              files: ["jquery-3.4.1.min.js"]
            }, function() {
              chrome.scripting.executeScript({target: { tabId: t.id },
                func: (title) => { self.title = title; },
                args: [changeInfo.title]
              }, function() {
                chrome.scripting.executeScript({target: { tabId: t.id }, 
                  files: ["insert_update.js"]});
                })
           });
          }
        })
      });
    }
  }
}

chrome.tabs.onUpdated.addListener(f)