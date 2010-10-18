/*
 * Copyright (C) 2010 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.apps.tag.message;

import com.android.apps.tag.record.UriRecord;
import com.google.common.base.Preconditions;

import java.util.Locale;

/**
 * A {@link ParsedNdefMessage} consisting of one {@link UriRecord}.
 */
class UriMessage implements ParsedNdefMessage {

    private final UriRecord mRecord;

    UriMessage(UriRecord record) {
        mRecord = Preconditions.checkNotNull(record);
    }

    @Override
    public String getSnippet(Locale locale) {
        // URIs cannot be localized
        return mRecord.getUri().toString();
    }

    @Override
    public boolean isStarred() {
        return false;
    }
}