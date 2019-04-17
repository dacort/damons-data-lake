#!/bin/sh
#
#
# Poor man's version. Good 'ol bash and shell commands.

# Initialize stat counters
COPIES=0
FROM_APPS=()
TO_APPS=()

# Get the current foreground app display name
getAppName() {
  lsappinfo info -only name `lsappinfo front` | cut -f 2 -d= | tr -d '"'
}

# Get Chrome tab URL
getChromeURL() {
  osascript -e 'tell application "Google Chrome" to return URL of active tab of front window'
  # For iTerm2...kind of works
  # osascript -e 'tell application "iTerm2" to return name of current window'
  # Could install shell integration: https://stackoverflow.com/questions/25051288/get-iterm-location-applescript
  # Something like this works!
  # lsof -a -p $(lsof -a -c zsh -d 0 -n | grep $(osascript -e 'tell application "iTerm2" to return the tty of the current session of the current window';) | awk '{print $2}')  -d cwd -n
  # https://stackoverflow.com/questions/5290299/applescript-how-to-get-the-current-directory-of-the-topmost-terminal
}

# Get the current clipboard contents
getClipboard() {
  pbpaste
}

# Increment stats every time a paste event happens
incStats() {
  FROM_APP=$1
  TO_APP=$2

  FROM_APPS[$COPIES]=$FROM_APP
  TO_APPS[$COPIES]=$TO_APP
  COPIES=$((COPIES+1))

  # Increment app copied *from*
  # Increment app copied *to*
  # Increment total number of copies
  # OR
  # Just keep a log and generate stats on the fly
}

# Send to Kinesis
trackEvent() {
  FROM_APP=$1
  TO_APP=$2

  # Only do this if STREAM_NAME is defined
  if [ ! ${STREAM_NAME} ]; then return; fi

  CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  aws kinesis put-record --stream-name ${STREAM_NAME} --data '{"event":"clipboard_copy","type":"counter","value":"1", "ts":"'${CURRENT_TIME}'", "metadata":{"clipboard":{"source":"'"${FROM_APP}"'","destination":"'"${TO_APP}"'"}}}
' --partition-key 2 > /dev/null &
  # echo '{"event":"clipboard_copy","type":"counter","value":"1","ts":"'${CURRENT_TIME}'", "metadata":{"clipboard":{"source":"'${FROM_APP}'","destination":"'${TO_APP}'"}}}'
}

# When Ctrl-C is pressed, print stats about clipboard usage
# If Ctrl-C hit twice, exit.
trap ctrl_c INT

function ctrl_c() {
  NOW=$(date "+%s")

  #   Has CTRL_C_PRESSED been pressed again within 5 seconds?
  #     Exit!
  #   If not
  #     Show stats
  #     Set current state
  #
  if [ $((NOW-CTRL_C_PRESSED)) -lt 5 ]; then
    echo "Quitting... 👋"
    exit 0
  else
    printStats
    echo "💁 Press Ctrl-C again to Quit\n"
    CTRL_C_PRESSED=$NOW
  fi
}

# Example:
# Total Copies:
#   Today: 15
#   All-Time: 300
# Top Copied Apps:
#    Google Chrome: 4
#    Slack: 2
# Top Pasted Apps:
#    Atom: 12
#    Google Chrome: 3
function printStats() {
  echo "\n📋  ---- CLIP STATS ---- 🌟"
  echo "Total Copies: $COPIES"

  echo "\nTop 5 Copied Apps:"
  for app in "${FROM_APPS[@]}" ; do
    KEY="${app%%:*}"
    VALUE="${app##*:}"
    echo "$VALUE"
  done | sort | uniq -c | sort -rn | head -n 5

  echo "\nTop 5 Pasted Apps:"
  for app in "${TO_APPS[@]}" ; do
    KEY="${app%%:*}"
    VALUE="${app##*:}"
    echo "$VALUE"
  done | sort | uniq -c | sort -rn | head -n 5

  echo
}

# Initialize clipboard contents and current app
CURR_TEXT=$(getClipboard)
CURR_APP=$(getAppName)

echo "Beginning monitoring, press Ctrl-C to show current stats\n\n"

# Run forever, sleeping 100ms at a time.
# If the clipboard content changes, start polling for a new foreground app.
# Poll every 300ms. If the foreground app doesnt change in 3 seconds,
# assume the contents were pasted into the same app.
while true; do
  PREV_TEXT=$CURR_TEXT
  CURR_TEXT=$(getClipboard)

  PREV_APP=$CURR_APP
  CURR_APP=$(getAppName)

  if [ "$PREV_TEXT" != "$CURR_TEXT" ]; then
    COUNTER=0
    while [ $COUNTER -lt 10 ] && [ "$PREV_APP" = "$CURR_APP" ]; do
      CURR_APP=$(getAppName)
      sleep 0.3
      COUNTER=$((COUNTER+1))
    done

    incStats "$PREV_APP" "$CURR_APP"
    echo "$COPIES: Copy $PREV_APP to $CURR_APP"
    trackEvent "$PREV_APP" "$CURR_APP"
  fi
  sleep 0.1
done
