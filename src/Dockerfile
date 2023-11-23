# Use the official .NET SDK image to build the application
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src

# Copy csproj and restore as a distinct layer
COPY ["AquaHub.NConsole/AquaHub.NConsole.csproj", "AquaHub.NConsole/"]
RUN dotnet restore "AquaHub.NConsole/AquaHub.NConsole.csproj"

# Copy the rest of the source code
COPY . .
WORKDIR "/src/AquaHub.NConsole"

# Build the project
RUN dotnet build "AquaHub.NConsole.csproj" -c Release -o /app/build

# Publish the project
FROM build AS publish
RUN dotnet publish "AquaHub.NConsole.csproj" -c Release -o /app/publish

# Generate the final image using the official .NET runtime image
FROM mcr.microsoft.com/dotnet/runtime:6.0 AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Set the command to run the application
ENTRYPOINT ["dotnet", "AquaHub.NConsole.dll"]