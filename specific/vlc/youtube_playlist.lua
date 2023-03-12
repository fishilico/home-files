    --[[
     Youtube playlist importer for VLC media player 1.1 and 2.0
     Copyright 2012 Guillaume Le Maout

     Authors:  Guillaume Le Maout
     Contact: https://addons.videolan.org/messages/?action=newmessage&username=exebetche

     This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

     This program is distributed in the hope that it will be useful,
     but WITHOUT ANY WARRANTY; without even the implied warranty of
     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
     GNU General Public License for more details.

     You should have received a copy of the GNU General Public License
     along with this program; if not, write to the Free Software
     Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
    --]]

    --[[
     MODified by Kai Gillmann, 19.01.2013, kaigillmann@googlemail.com:
     VLC HAS already a youtube importer, but not for playlists. IMO this mentioned one is
     better than this one, because it opens the video in the best possible video resolution.
     So i decided to remove all parts of the code which is not responsible for list handling.
     Now this lua script parses the list, as wanted, but for each video opened, the vlc default
     Youtube script is used, so the videos will be displayed properly.
    --]]

    -- Helper function to get a parameter's value in a URL
    function get_url_param( url, name )
        local _, _, res = string.find( url, "[&?]"..name.."=([^&]*)" )
        return res
    end

    -- Probe function.
    function probe()
        if vlc.access ~= "http" and vlc.access ~= "https" then
            return false
        end

        return string.match(vlc.path:match("([^/]+)"),"%w+.youtube.com") and (string.match(vlc.path, "list="))
    end

    -- Parse function.
    function parse()
            if string.match( vlc.path, "list=" ) then
                    local p = {}
                    local playlistID = get_url_param( vlc.path, "list" )
                    local videoID = get_url_param( vlc.path, "v" )
                    local playlistURL = "https://www.youtube.com/list_ajax?action_get_list=1&style=xml&list="..playlistID
                    local s = vlc.stream(playlistURL)
                    local playlistData = ""
                    local line = ""
                    while line do
                            playlistData = playlistData..line
                            line = s:readline()
                    end

                    local playlist_parsed = parse_xml(playlistData).root.video

                    for i, video in ipairs(playlist_parsed) do
                            local item = {}
                            item.path = "https://www.youtube.com/watch?v="..video.encrypted_id.CDATA
                            item.title = video.title.CDATA
                            item.artist = video.author.CDATA
                            item.arturl = video.thumbnail.CDATA
                            --~ item.description = video.description
                            --~ item.rating = video.rating
                            table.insert (p, item)
                    end
                    return p
        end
    end


    function parse_xml(data)
            local tree = {}
            local stack = {}
            local tmp = {}
            local tmpTag = ""
            local level = 0

            table.insert(stack, tree)

            for op, tag, attr, empty, val in string.gmatch(data, "<(%p?)([^%s>/]+)([^>]-)(%/?)>[%s\r\n\t]*([^<]*)[%s\r\n\t]*") do
                    if op=="?" then
                            --~ DOCTYPE
                    elseif op=="/" then
                            if level>0 then
                                    level = level - 1
                                    table.remove(stack)
                            end
                    else
                            level = level + 1

                            if op=="!" then
                                    stack[level]['CDATA'] = vlc.strings.resolve_xml_special_chars(string.gsub(tag..attr, "%[CDATA%[(.+)%]%]", "%1"))
                                    attr = ""
                                    level = level - 1
                            elseif type(stack[level][tag]) == "nil" then
                                    stack[level][tag] = {}
                                    table.insert(stack, stack[level][tag])
                            else
                                    if type(stack[level][tag][1]) == "nil" then
                                            tmp = nil
                                            tmp = stack[level][tag]
                                            stack[level][tag] = nil
                                            stack[level][tag] = {}
                                            table.insert(stack[level][tag], tmp)
                                    end
                                    tmp = nil
                                    tmp = {}
                                    table.insert(stack[level][tag], tmp)
                                    table.insert(stack, tmp)
                            end

                            if val~="" then
                                    stack[level][tag]['CDATA'] = {}
                                    stack[level][tag]['CDATA'] = vlc.strings.resolve_xml_special_chars(val)
                            end

                            if attr ~= "" then
                                    stack[level][tag]['ATTR'] = {}
                                    string.gsub(attr, "(%w+)=[\"'](.-)[\"']", function (name, value)
                                            stack[level][tag]['ATTR'][name] = value
                                    end)
                            end

                            if empty ~= "" then
                                    level = level - 1
                                    table.remove(stack)
                            end
                    end
            end
            return tree
    end
