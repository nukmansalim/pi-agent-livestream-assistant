#!/bin/bash
# Pi Agent YouTube API Bash Client
# Usage: ./pi_agent_bash_client.sh <command> [args...]

BASE_URL="http://localhost:5000"
USER_ID="${PI_AGENT_USER_ID:-default_user}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper function to make API calls
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"

    if [ "$method" = "GET" ]; then
        curl -s -X GET "$BASE_URL$endpoint" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
    else
        echo "$data" | curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d @- | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
    fi
}

# Check API health
check_health() {
    echo -e "${YELLOW}🔍 Checking API health...${NC}"
    api_call "GET" "/health"
}

# Check YouTube authentication status
check_status() {
    local user="${1:-$USER_ID}"
    echo -e "${YELLOW}🔐 Checking YouTube auth status for user: $user${NC}"
    api_call "GET" "/status?user_id=$user"
}

# Upload video
upload_video() {
    local file_path="$1"
    local title="$2"
    local description="${3:-}"
    local tags="${4:-}"
    local privacy="${5:-private}"

    if [ -z "$file_path" ] || [ -z "$title" ]; then
        echo -e "${RED}❌ Usage: $0 upload <file_path> <title> [description] [tags] [privacy]${NC}"
        return 1
    fi

    # Convert comma-separated tags to JSON array
    local tags_json="[]"
    if [ -n "$tags" ]; then
        tags_json=$(echo "$tags" | tr ',' '\n' | sed 's/.*/"&"/' | paste -sd, - | sed 's/.*/[&]/')
    fi

    local data="{
        \"user_id\": \"$USER_ID\",
        \"file_path\": \"$file_path\",
        \"title\": \"$title\",
        \"description\": \"$description\",
        \"tags\": $tags_json,
        \"privacy\": \"$privacy\"
    }"

    echo -e "${YELLOW}📤 Uploading video: $title${NC}"
    api_call "POST" "/upload" "$data"
}

# Edit video
edit_video() {
    local video_id="$1"
    local title="$2"
    local description="$3"
    local privacy="$4"

    if [ -z "$video_id" ]; then
        echo -e "${RED}❌ Usage: $0 edit <video_id> [title] [description] [privacy]${NC}"
        return 1
    fi

    local data="{
        \"user_id\": \"$USER_ID\",
        \"video_id\": \"$video_id\",
        \"title\": \"$title\",
        \"description\": \"$description\",
        \"privacy\": \"$privacy\"
    }"

    echo -e "${YELLOW}✏️ Editing video: $video_id${NC}"
    api_call "POST" "/edit" "$data"
}

# Execute natural language command
execute_command() {
    local command="$*"

    if [ -z "$command" ]; then
        echo -e "${RED}❌ Usage: $0 execute <natural language command>${NC}"
        return 1
    fi

    local data="{
        \"user_id\": \"$USER_ID\",
        \"command\": \"$command\"
    }"

    echo -e "${YELLOW}🤖 Executing: $command${NC}"
    api_call "POST" "/execute" "$data"
}

# Show capabilities
show_capabilities() {
    echo -e "${YELLOW}📋 Getting API capabilities...${NC}"
    api_call "GET" "/capabilities"
}

# Show help
show_help() {
    echo "Pi Agent YouTube API Bash Client"
    echo ""
    echo "Usage: $0 <command> [arguments...]"
    echo ""
    echo "Commands:"
    echo "  health                    Check API health"
    echo "  status [user_id]          Check YouTube auth status"
    echo "  capabilities              Show API capabilities"
    echo "  upload <file> <title> [desc] [tags] [privacy]  Upload video"
    echo "  edit <video_id> [title] [desc] [privacy]       Edit video"
    echo "  execute <command>         Execute natural language command"
    echo "  help                      Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  PI_AGENT_USER_ID          Default user ID (default: default_user)"
    echo ""
    echo "Examples:"
    echo "  $0 health"
    echo "  $0 status my_user"
    echo "  $0 upload /path/video.mp4 'My Video' 'Description' 'tag1,tag2' private"
    echo "  $0 edit dQw4w9WgXcQ 'New Title'"
    echo "  $0 execute 'upload video from /path/video.mp4 titled Tutorial'"
}

# Main command dispatcher
case "${1:-help}" in
    health)
        check_health
        ;;
    status)
        check_status "$2"
        ;;
    capabilities)
        show_capabilities
        ;;
    upload)
        shift
        upload_video "$@"
        ;;
    edit)
        shift
        edit_video "$@"
        ;;
    execute)
        shift
        execute_command "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac