unread_count() {
    osascript -e 'tell application "Microsoft Outlook" to unread count of folder "Inbox" of default account'
}

chrome_tabs() {
    osascript -e 'tell application "Google Chrome" to count every tab of every window'
}

iterm_tabs() {
    osascript -e 'tell application "iTerm" to count every tab of every window' 
}

# Gather various stats and report them to Kinesis stream
while true; do
    UNREAD_COUNT=$(unread_count)
    CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "Unread emails: ${UNREAD_COUNT}"
    aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"outlook_unread","type":"gauge","value":"'${UNREAD_COUNT}'", "ts":"'${CURRENT_TIME}'"}
' --partition-key 1

    CHROME_TABS=$(chrome_tabs)
    echo "Chrome tabs: ${CHROME_TABS}"
    aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"chrome_tabs","type":"gauge","value":"'${CHROME_TABS}'", "ts":"'${CURRENT_TIME}'"}
' --partition-key 1

    ITERM_TABS=$(iterm_tabs)
    echo "iTerm tabs: ${ITERM_TABS}"
    aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"iterm_tabs","type":"gauge","value":"'${ITERM_TABS}'", "ts":"'${CURRENT_TIME}'"}
' --partition-key 1
    sleep 60
done
