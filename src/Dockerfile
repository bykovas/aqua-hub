# Use the official .NET SDK image for ARM architecture to build the application
FROM mcr.microsoft.com/dotnet/sdk:6.0-bullseye-slim-arm32v7 AS build
WORKDIR /src

# List installed .NET SDK versions
RUN dotnet --list-sdks

# Copy csproj and restore as a distinct layer
COPY ["AquaHub.NConsole/AquaHub.NConsole.csproj", "AquaHub.NConsole/"]
RUN dotnet restore "AquaHub.NConsole/AquaHub.NConsole.csproj" --source "https://api.nuget.org/v3/index.json"

# Copy the rest of the source code
COPY . .
WORKDIR "/src/AquaHub.NConsole"

# Build the project for ARM
RUN dotnet build "AquaHub.NConsole.csproj" -c Release -o /app/build -r linux-arm

# Publish the project for ARM
FROM build AS publish
RUN dotnet publish "AquaHub.NConsole.csproj" -c Release -o /app/publish -r linux-arm

# Generate the final image using the official .NET runtime image for ARM
FROM mcr.microsoft.com/dotnet/runtime:6.0-bullseye-slim-arm32v7 AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Set the command to run the application
ENTRYPOINT ["dotnet", "AquaHub.NConsole.dll"]